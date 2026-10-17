import streamlit as st
import hashlib
import datetime
import calendar
import pandas as pd

try:
    from zoneinfo import ZoneInfo
    TZ_PARIS = ZoneInfo("Europe/Paris")
except Exception:
    TZ_PARIS = datetime.timezone.utc

# ==============================================================================
# CONFIGURATION & IDENTITÉ VISUELLE – CABINET REPLIK
# ==============================================================================
st.set_page_config(
    page_title="Cabinet Replik | Plus vite que la viralité",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.replik-header {background: linear-gradient(135deg, #0f1226 0%, #1e1b4b 65%, #e61e6e 100%);
  padding: 22px 28px; border-radius: 12px; color: white; margin-bottom: 18px;}
.badge-role {background-color: rgba(255,255,255,0.18); color: #fff; padding: 4px 12px;
  border-radius: 20px; font-size: 0.8em; font-weight: 600; letter-spacing: 0.5px;}
.cert-box {font-family: 'Courier New', monospace; background-color: #0f1226; color: #10b981;
  padding: 18px; border-radius: 10px; border-left: 5px solid #e61e6e; font-size: 0.86em;
  line-height: 1.6; word-break: break-all;}
.kpi {border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 16px; height: 100%;
  min-height: 112px; background: #ffffff; overflow-wrap: anywhere;}
.kpi-label {font-size: 0.80em; color: #64748b; text-transform: uppercase; letter-spacing: 0.4px;}
.kpi-value {font-size: 1.30em; font-weight: 700; color: #0f1226; margin: 4px 0 2px 0; line-height: 1.25;}
.kpi-sub {font-size: 0.82em; color: #475569;}
.kpi-alert {border-color: #e61e6e; border-left: 5px solid #e61e6e; background: #fdf2f8;}
.kpi-warn {border-color: #f59e0b; border-left: 5px solid #f59e0b; background: #fffbeb;}
.kpi-ok {border-color: #10b981; border-left: 5px solid #10b981; background: #ecfdf5;}
.step {padding: 12px 8px; border-radius: 8px; text-align: center; height: 100%; font-size: 0.92em;}
.step-done {background:#ecfdf5; border:1px solid #10b981; border-top:4px solid #10b981;}
.step-active {background:#fdf2f8; border:1px solid #e61e6e; border-top:4px solid #e61e6e;}
.step-wait {background:#f8fafc; border:1px solid #cbd5e1; border-top:4px solid #94a3b8; color:#64748b;}
.step-actor {font-size: 0.72em; letter-spacing: 1px; font-weight: 700; color: #64748b;}
.devis {border: 2px solid #1e1b4b; border-radius: 10px; padding: 14px 18px; background: #f8fafc;}
.devis-prix {font-size: 1.6em; font-weight: 800; color: #1e1b4b;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# GRILLE TARIFAIRE (fidèle aux slides 19 à 22)
# ==============================================================================
PROFILS = {
    "PART": "Particulier – demande ponctuelle",
    "ENT": "Entreprise / marque – demande ponctuelle",
    "P1": "Abonné Prévention P1 Particulier",
    "P2": "Abonné Prévention P2 Personnalité",
    "P3": "Abonné Prévention P3 Entreprise",
}
ABONNEMENTS = {  # € HT / mois par niveau 1, 2, 3
    "P1": {1: 29, 2: 39, 3: 59},
    "P2": {1: 249, 2: 349, 3: 449},
    "P3": {1: 229, 2: 299, 3: 369},
}
NIVEAUX = {1: "Niveau 1 · Veille", 2: "Niveau 2 · Preuve", 3: "Niveau 3 · Justice"}
SIGNALEMENTS_INCLUS = {"P1": {1: 2, 2: 6, 3: 12}, "P2": {1: 15, 2: 15, 3: 25}, "P3": {1: 15, 2: 15, 3: 25}}
FORMULES = {
    "R1": "R1 Essentiel – signalement aux plateformes, suivi du retrait, 1 semaine de veille",
    "R2": "R2 Preuve horodatée – R1 + capture certifiée inaltérable, rapport de preuve conservé 5 ans",
    "R3": "R3 Preuve authentique – R1 + constat de commissaire de justice d’astreinte 24h/24",
    "R4": "R4 Retrait judiciaire – mise en demeure puis référé devant le tribunal judiciaire, avec astreinte",
}
JUSTICE = {
    "J1": "J1 Justice civile – dommages-intérêts (2 800 à 5 150 € HT)",
    "J2A": "J2A Citation directe – auteur identifié (2 700 à 4 200 € HT)",
    "J2B": "J2B Plainte au procureur – auteur inconnu (700 à 1 000 € HT)",
    "J2C": "J2C Partie civile directe – délits de presse et crimes (3 800 à 7 200 € HT)",
}


def eur(x):
    return f"{x:,.0f}".replace(",", " ") + " €"


def calcul_devis(profil, niveau, formule, nuit):
    """Retourne (min, max, détail, majoration) en € HT selon la grille des slides."""
    abonne = profil in ABONNEMENTS
    majo = 0
    if nuit:
        if abonne:
            majo = 20
        elif formule in ("R1", "R2"):
            majo = 75
        elif formule == "R3":
            majo = 150
    if not abonne:
        base = {"R1": (125, 125), "R2": (150, 150), "R3": (320, 320), "R4": (1700, 2650)}[formule]
        detail = "Forfait ponctuel, frais de tiers inclus"
    else:
        credits = SIGNALEMENTS_INCLUS[profil][niveau]
        if formule == "R1":
            base, detail = (0, 0), f"Signalement décompté de vos {credits} signalements inclus / mois"
        elif formule == "R2":
            base = (15, 15) if niveau == 1 else (0, 0)
            detail = "Capture horodatée à 15 € l’unité (niveau 1)" if niveau == 1 else "Capture horodatée incluse dans votre abonnement"
        elif formule == "R3":
            prix = {1: 250, 2: 230, 3: 0}[niveau]
            base = (prix, prix)
            detail = "Constat inclus (2 par an, puis 210 €)" if niveau == 3 else f"Constat de commissaire au tarif abonné ({prix} €)"
        else:
            remise = {1: 0, 2: 0.15, 3: 0.25}[niveau]
            base = (1700 * (1 - remise), 2650 * (1 - remise))
            detail = "Plein tarif (niveau 1)" if niveau == 1 else f"Remise abonné de {int(remise * 100)} % sur la mise en demeure et le référé"
    return base[0] + majo, base[1] + majo, detail, majo


def libelle_prix(lo, hi):
    if hi == 0:
        return "Inclus"
    return eur(lo) + " HT" if lo == hi else f"{eur(lo)} à {eur(hi)} HT"


# ==============================================================================
# 10 FAUX SIGNALEMENTS (slide 18 : « Tester »)
# regime : presse (L. 1881, 3 mois) · penal (délit de droit commun, 6 ans) · civil (5 ans) · mixte
# ==============================================================================
DOSSIERS_TYPES = [
    {
        "id": "RPK-2026-01", "titre": "Deepfake sexuel",
        "label": "Cas 1 – Montage deepfake à caractère sexuel (particulier, auteur anonyme, nuit)",
        "client": "Clara M.", "profil": "PART", "niveau": None, "pack_proches": False,
        "formule": "R3", "plateforme": "Telegram et site web tiers", "url": "https://t.me/channel_archive_fr/98234",
        "jours_pub": 3, "auteur_connu": False, "auteur_nom": "", "urgence_nuit": True, "discretion": True, "mineur": False,
        "faits": "Diffusion sans consentement d’un montage hypertruqué (deepfake) à caractère sexuel utilisant le visage de la cliente, associé à son nom réel et à celui de son établissement.",
        "ia_qualification": "Montage à caractère sexuel réalisé sans consentement (art. 226-8-1 C. pén. : 2 ans et 60 000 €, portés à 3 ans et 75 000 € en cas de diffusion en ligne).",
        "regime": "penal",
        "ia_actions": "Empreinte SHA-256 des pièces, pré-remplissage de la notification DSA (art. 16) et du signalement PHAROS, recherche des republications (veille 7 jours).",
        "avocat_arbitrage": "Commande du constat de commissaire d’astreinte (R3), plainte contre X au procureur (J2B) avec demande de réquisitions aux plateformes.",
        "justice": "J2B", "actes": ["DSA", "PLAINTE", "REQ145"],
    },
    {
        "id": "RPK-2026-02", "titre": "Raid de faux avis",
        "label": "Cas 2 – Raid coordonné de faux avis Google (entreprise abonnée P3)",
        "client": "SAS Clinique Lumière", "profil": "P3", "niveau": 2, "pack_proches": False,
        "formule": "R4", "plateforme": "Google Maps (fiche établissement)", "url": "https://maps.google.com/reviews/clinique_lumiere_id88",
        "jours_pub": 14, "auteur_connu": False, "auteur_nom": "", "urgence_nuit": False, "discretion": False, "mineur": False,
        "faits": "Publication coordonnée de 12 avis 1 étoile en deux heures : « Clinique insalubre, produits périmés dangereux, la directrice falsifie ses diplômes ! »",
        "ia_qualification": "Dénigrement (art. 1240 C. civ.) pour les propos visant les prestations (« insalubre », « produits périmés ») ; diffamation publique envers un particulier (art. 29 al. 1 et 32 L. 29 juill. 1881) pour l’accusation visant la directrice (« falsifie ses diplômes »).",
        "regime": "mixte",
        "ia_actions": "Détection de l’anomalie temporelle (12 avis en 2 h), capture horodatée incluse (P3 niveau 2), préparation de la notification DSA et du projet de référé.",
        "avocat_arbitrage": "Distinguer les propos : art. 1240 pour les prestations, loi de 1881 pour la personne de la directrice (aucune requalification possible – Ass. plén., 12 juill. 2000). Référé aux fins de suppression et d’identification des auteurs.",
        "justice": "J1", "actes": ["DSA", "REFERE", "REQ145"],
    },
    {
        "id": "RPK-2026-03", "titre": "Voix clonée",
        "label": "Cas 3 – Voix clonée par IA et faux profil d’influenceur (personnalité abonnée P2)",
        "client": "Lucas « SkyVibe » (créateur de contenu)", "profil": "P2", "niveau": 3, "pack_proches": False,
        "formule": "R3", "plateforme": "TikTok et Instagram Reels", "url": "https://tiktok.com/@skyvibe_invest_officiel/video/778899",
        "jours_pub": 1, "auteur_connu": False, "auteur_nom": "", "urgence_nuit": True, "discretion": True, "mineur": False,
        "faits": "Vidéo utilisant un clone vocal généré par IA et l’image du client pour promouvoir une escroquerie financière auprès de sa communauté.",
        "ia_qualification": "Hypertrucage sans consentement (art. 226-8 C. pén., issu de la loi SREN) ; usurpation d’identité numérique (art. 226-4-1 C. pén.) ; escroquerie au préjudice des abonnés (art. 313-1 C. pén.) – à apprécier.",
        "regime": "penal",
        "ia_actions": "Alerte remontée par l’IA de veille du prestataire, figeage probatoire, préparation des notifications d’urgence Meta et TikTok.",
        "avocat_arbitrage": "Coordination confidentielle avec l’agent (prévention de l’effet Streisand) ; message de prévention à la communauté à valider ; constat R3 inclus (2 par an).",
        "justice": "J2B", "actes": ["DSA", "PLAINTE", "REQ145"],
    },
    {
        "id": "RPK-2026-04", "titre": "Images intimes (ex-conjoint)",
        "label": "Cas 4 – Diffusion d’images intimes par un ex-conjoint identifié (nuit)",
        "client": "Sarah L.", "profil": "PART", "niveau": None, "pack_proches": False,
        "formule": "R3", "plateforme": "Instagram et messagerie", "url": "https://instagram.com/p/post_id_88219",
        "jours_pub": 2, "auteur_connu": True, "auteur_nom": "M. [ex-conjoint – identité communiquée par la cliente]",
        "urgence_nuit": True, "discretion": True, "mineur": False,
        "faits": "Mise en ligne par l’ex-conjoint de photographies intimes sans consentement, avec identification des proches de la victime.",
        "ia_qualification": "Diffusion sans consentement d’images à caractère sexuel (art. 226-2-1 C. pén. : 2 ans et 60 000 €).",
        "regime": "penal",
        "ia_actions": "Traitement intégralement local (aucune exposition externe des images), empreinte SHA-256, préparation de la notification de retrait immédiat.",
        "avocat_arbitrage": "Auteur identifié : citation directe (J2A) ou plainte, à arbitrer au regard de la sécurité de la cliente ; si violences, envisager une ordonnance de protection (art. 515-9 C. civ.).",
        "justice": "J2A", "actes": ["DSA", "CITATION", "PLAINTE"],
    },
    {
        "id": "RPK-2026-05", "titre": "Doxxing",
        "label": "Cas 5 – Cyberharcèlement en meute et divulgation d’adresse (abonné P1)",
        "client": "Mehdi K.", "profil": "P1", "niveau": 2, "pack_proches": False,
        "formule": "R2", "plateforme": "X (Twitter)", "url": "https://x.com/thread_attaque/status/189273645",
        "jours_pub": 5, "auteur_connu": False, "auteur_nom": "", "urgence_nuit": False, "discretion": False, "mineur": False,
        "faits": "Publication de l’adresse personnelle et du numéro de téléphone du client, accompagnée d’appels à venir l’intimider à son domicile.",
        "ia_qualification": "Révélation d’informations personnelles exposant à un risque (art. 223-1-1 C. pén. : 3 ans et 45 000 €) ; harcèlement moral en ligne (art. 222-33-2-2 C. pén.).",
        "regime": "penal",
        "ia_actions": "Agrégation des messages du raid dans un rapport horodaté unique, préparation des signalements groupés.",
        "avocat_arbitrage": "Qualification du péril : conseils de sécurité immédiats, plainte au parquet (pôle national de lutte contre la haine en ligne si raid de masse).",
        "justice": "J2B", "actes": ["DSA", "PLAINTE"],
    },
    {
        "id": "RPK-2026-06", "titre": "Diffamation LinkedIn",
        "label": "Cas 6 – Post LinkedIn diffamatoire d’un concurrent identifié (dirigeant abonné P3)",
        "client": "Jean-Marc V. (dirigeant de société)", "profil": "P3", "niveau": 1, "pack_proches": False,
        "formule": "R3", "plateforme": "LinkedIn", "url": "https://linkedin.com/posts/concurrent_99283",
        "jours_pub": 45, "auteur_connu": True, "auteur_nom": "[Dirigeant de la société concurrente]",
        "urgence_nuit": False, "discretion": False, "mineur": False,
        "faits": "Publication publique d’un concurrent accusant nommément le dirigeant de détournement de fonds sociaux et de fraude fiscale.",
        "ia_qualification": "Diffamation publique envers un particulier (art. 29 al. 1 et 32 L. 29 juill. 1881).",
        "regime": "presse",
        "ia_actions": "Calcul de l’échéance de prescription (3 mois), figeage de l’URL, extraction des informations de l’auteur.",
        "avocat_arbitrage": "Auteur identifié : citation directe (J2A, plus rapide) ou plainte avec constitution de partie civile (J2C). Articulation et qualification des faits (art. 53) ; anticiper l’offre de preuve (art. 55, 10 jours).",
        "justice": "J2C", "actes": ["CITATION", "CPC", "DSA"],
    },
    {
        "id": "RPK-2026-07", "titre": "Usurpation d’identité",
        "label": "Cas 7 – Faux compte usurpant l’identité d’une élue locale (abonnée P2)",
        "client": "Hélène R.", "profil": "P2", "niveau": 2, "pack_proches": False,
        "formule": "R4", "plateforme": "Facebook et TikTok", "url": "https://facebook.com/profile.php?id=1000998877",
        "jours_pub": 4, "auteur_connu": False, "auteur_nom": "", "urgence_nuit": False, "discretion": False, "mineur": False,
        "faits": "Création d’une page imitant le compte officiel de la cliente et diffusant de fausses prises de position publiques.",
        "ia_qualification": "Usurpation d’identité numérique (art. 226-4-1 C. pén. : 1 an et 15 000 €).",
        "regime": "penal",
        "ia_actions": "Détection par la veille d’image du prestataire, capture horodatée incluse, préparation de la notification Meta et TikTok.",
        "avocat_arbitrage": "Mise en demeure puis référé aux fins de suppression sous astreinte et de communication des données d’identification ; plainte en parallèle.",
        "justice": "J2B", "actes": ["DSA", "MED", "REFERE", "REQ145"],
    },
    {
        "id": "RPK-2026-08", "titre": "Sextorsion",
        "label": "Cas 8 – Chantage à la vidéo intime – sextorsion en cours (nuit)",
        "client": "Thomas B.", "profil": "PART", "niveau": None, "pack_proches": False,
        "formule": "R2", "plateforme": "Instagram et Discord", "url": "https://discord.com/channels/9988776655",
        "jours_pub": 0, "auteur_connu": False, "auteur_nom": "", "urgence_nuit": True, "discretion": True, "mineur": False,
        "faits": "Menace de diffuser un enregistrement intime à la liste de contacts de la victime à défaut d’un virement immédiat de 800 €.",
        "ia_qualification": "Chantage (art. 312-10 C. pén. : 5 ans et 75 000 €).",
        "regime": "penal",
        "ia_actions": "Figeage des captures et des identifiants des comptes, envoi immédiat des consignes de sécurité au client.",
        "avocat_arbitrage": "Rappel au client : ne pas payer, ne pas supprimer les échanges, cesser tout contact. Signalement des comptes, demande de suspension, plainte.",
        "justice": "J2B", "actes": ["DSA", "PLAINTE"],
    },
    {
        "id": "RPK-2026-09", "titre": "Diffamation prescrite",
        "label": "Cas 9 – Article diffamatoire publié il y a 105 jours (prescription de 3 mois acquise)",
        "client": "SARL Atelier Architecture Horizon", "profil": "ENT", "niveau": None, "pack_proches": False,
        "formule": "R2", "plateforme": "Blog professionnel", "url": "https://blog-urbanisme-info.fr/atelier-horizon",
        "jours_pub": 105, "auteur_connu": True, "auteur_nom": "[Éditeur du blog]",
        "urgence_nuit": False, "discretion": False, "mineur": False,
        "faits": "Publication, il y a plus de trois mois, d’un billet accusant l’entreprise de livrer des chantiers non conformes et dangereux.",
        "ia_qualification": "Diffamation publique envers une personne morale (art. 29 al. 1 et 32 L. 1881) – PRESCRIPTION ACQUISE (art. 65 L. 1881 : 3 mois à compter de la première mise en ligne).",
        "regime": "presse",
        "ia_actions": "Détection automatique de l’expiration du délai et verrouillage des actes pénaux fondés sur la loi de 1881.",
        "avocat_arbitrage": "Valeur ajoutée de l’avocat : réorientation possible sur le dénigrement (art. 1240 C. civ., prescription de 5 ans) uniquement si les propos visent les prestations et non l’honneur de la société ; à défaut, pas d’action au fond (Ass. plén., 12 juill. 2000). Retrait amiable toujours possible.",
        "justice": "J1", "actes": ["DSA", "MED", "REFERE"],
    },
    {
        "id": "RPK-2026-10", "titre": "Harcèlement d’un mineur",
        "label": "Cas 10 – Harcèlement visant l’enfant mineur d’une cliente (option Pack Proches)",
        "client": "Mme Claire D. (pour son fils mineur)", "profil": "P2", "niveau": 2, "pack_proches": True,
        "formule": "R2", "plateforme": "TikTok et Snapchat", "url": "https://tiktok.com/@video_college_92/video/112233",
        "jours_pub": 2, "auteur_connu": True, "auteur_nom": "[Élèves identifiés – mineurs]",
        "urgence_nuit": False, "discretion": True, "mineur": True,
        "faits": "Diffusion d’une vidéo humiliante visant un collégien, repartagée sur plusieurs comptes secondaires.",
        "ia_qualification": "Harcèlement scolaire (art. 222-33-2-3 C. pén., loi du 2 mars 2022), aggravé par l’usage d’un service en ligne ; atteinte au droit à l’image (art. 9 C. civ.).",
        "regime": "penal",
        "ia_actions": "Identification de la vidéo source et de 4 comptes miroirs, capture horodatée, préparation des notifications prioritaires (protection des mineurs).",
        "avocat_arbitrage": "Auteurs mineurs : mise en demeure des représentants légaux (art. 1242 al. 4 C. civ.), information de l’établissement, signalement prioritaire (3018, signaleur de confiance).",
        "justice": "J2B", "actes": ["DSA", "MED", "PLAINTE"],
    },
]
LABELS = [d["label"] for d in DOSSIERS_TYPES]
PAR_LABEL = {d["label"]: d for d in DOSSIERS_TYPES}

# ==============================================================================
# OUTILS JURIDIQUES : PRESCRIPTION & QUALIFICATION SIMULÉE (IA LOCALE)
# ==============================================================================
def add_months(d, n):
    m = d.month - 1 + n
    y, m = d.year + m // 12, m - (m // 12) * 12 + 1
    return datetime.date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def prescription(ac):
    """Échéance selon le régime. Presse : 3 mois de date à date (art. 65 L. 1881)."""
    pub = datetime.date.today() - datetime.timedelta(days=ac["jours_pub"])
    if ac["regime"] in ("presse", "mixte"):
        fin = add_months(pub, 3)
        return {"court": True, "fin": fin, "restant": (fin - datetime.date.today()).days,
                "texte": "3 mois – art. 65 L. 1881"}
    if ac["regime"] == "civil":
        return {"court": False, "fin": add_months(pub, 60), "restant": None, "texte": "5 ans – art. 2224 C. civ."}
    return {"court": False, "fin": add_months(pub, 72), "restant": None, "texte": "6 ans – délit, art. 8 CPP"}


def presse_prescrite(ac):
    p = prescription(ac)
    return ac["regime"] == "presse" and p["court"] and p["restant"] < 0


REGLES = [  # (mots-clés, qualification, régime) – simulation pédagogique de l’IA locale
    (["chantage", "virement", "payer", "rançon"], "Chantage (art. 312-10 C. pén.)", "penal"),
    (["deepfake", "hypertruq", "montage", "clone", "généré par ia"], "Hypertrucage sans consentement (art. 226-8 C. pén. ; art. 226-8-1 si contenu sexuel)", "penal"),
    (["intime", "nue", "sexuel", "sextape"], "Diffusion sans consentement d’images à caractère sexuel (art. 226-2-1 C. pén.)", "penal"),
    (["adresse", "téléphone", "domicile"], "Révélation d’informations personnelles exposant à un risque (art. 223-1-1 C. pén.)", "penal"),
    (["faux compte", "usurp", "se fait passer", "imite"], "Usurpation d’identité numérique (art. 226-4-1 C. pén.)", "penal"),
    (["harcèle", "harcèlement", "meute", "raid"], "Harcèlement moral en ligne (art. 222-33-2-2 C. pén.)", "penal"),
    (["avis", "étoile"], "Dénigrement de prestations (art. 1240 C. civ.) – à distinguer d’une éventuelle diffamation", "civil"),
    (["accuse", "escroc", "voleur", "fraude", "détourn", "falsifi", "mensonge"], "Diffamation publique (art. 29 al. 1 et 32 L. 1881)", "presse"),
    (["insulte", "injure", "injurie"], "Injure publique (art. 29 al. 2 et 33 L. 1881)", "presse"),
]


def qualifier(texte):
    t = texte.lower()
    quals, regimes = [], set()
    for mots, qual, reg in REGLES:
        if any(m in t for m in mots):
            quals.append(qual)
            regimes.add(reg)
    if not quals:
        return "Aucune qualification certaine – à déterminer par l’avocat.", "penal"
    if "presse" in regimes and "civil" in regimes:
        reg = "mixte"
    elif "presse" in regimes:
        reg = "presse"
    elif "penal" in regimes:
        reg = "penal"
    else:
        reg = "civil"
    return " ; ".join(quals) + ".", reg


def maintenant():
    return datetime.datetime.now(TZ_PARIS).strftime("%d/%m/%Y à %H:%M:%S (heure de Paris)")


def ouvrir_dossier(d, **maj):
    ts = maintenant()
    data = {**d, **maj}
    empreinte = hashlib.sha256(f"REPLIK|{data['id']}|{data['client']}|{data['url']}|{ts}|{data['faits']}".encode("utf-8")).hexdigest()
    data.update({
        "timestamp": ts, "sha256": empreinte, "pieces": data.get("pieces", []),
        "statut": "qualifie", "avocat_signataire": "", "acte_final": "", "acte_code": "", "notes_internes": "",
    })
    return data


if "active_case" not in st.session_state:
    st.session_state.active_case = ouvrir_dossier(DOSSIERS_TYPES[0])
if "compteur" not in st.session_state:
    st.session_state.compteur = 100

# ==============================================================================
# MODÈLES D’ACTES PRÉ-RÉDIGÉS (slide 18 : « modèles d’actes pré-rédigés »)
# Les passages entre crochets sont à compléter ou à valider par l’avocat.
# ==============================================================================
ACTES = {
    "DSA": "Notification de contenu illicite à la plateforme (art. 16 DSA)",
    "MED": "Mise en demeure d’avocat (auteur ou hébergeur)",
    "REFERE": "Assignation en référé – suppression sous astreinte (R4)",
    "REQ145": "Requête aux fins d’identification de l’auteur (art. 145 CPC)",
    "PLAINTE": "Plainte au procureur de la République (J2B)",
    "CITATION": "Citation directe devant le tribunal correctionnel (J2A)",
    "CPC": "Plainte avec constitution de partie civile (J2C)",
}
ACTES_PENAUX = {"PLAINTE", "CITATION", "CPC"}


def entete(ac, avocat):
    return (f"CABINET REPLIK – Avocats au Barreau de Paris\n"
            f"Permanence 24h/24 – {avocat}\n"
            f"Réf. : {ac['id']} – {ac['client']}\n"
            f"Paris, le {datetime.date.today().strftime('%d/%m/%Y')}\n\n")


def preuve(ac):
    lignes = [f"– Accusé de signalement horodaté du {ac['timestamp']} (empreinte SHA-256 : {ac['sha256']})"]
    for p in ac["pieces"]:
        lignes.append(f"– Pièce « {p['nom']} » (empreinte SHA-256 : {p['sha']})")
    if ac["formule"] in ("R3", "R4"):
        lignes.append("– Procès-verbal de constat de commissaire de justice du [date] [à joindre]")
    elif ac["formule"] == "R2":
        lignes.append("– Capture certifiée horodatée et rapport de preuve [à joindre]")
    return "\n".join(lignes)


def rediger(code, ac, avocat):
    h = entete(ac, avocat)
    auteur = ac["auteur_nom"] or "[auteur non identifié]"
    presse = ac["regime"] in ("presse", "mixte")
    fondement_civil = presse_prescrite(ac)
    qual = ("Dénigrement (art. 1240 C. civ.) – [l’avocat vérifie que les propos visent les prestations et non l’honneur de la société]"
            if fondement_civil else ac["ia_qualification"])

    if code == "DSA":
        return h + f"""Destinataire : service de traitement des notifications – {ac['plateforme']}
[Canal : formulaire de notification de la plateforme + courriel au point de contact (art. 11 et 12 DSA)]

Objet : Notification de contenu illicite – article 16 du règlement (UE) 2022/2065 (DSA)

Madame, Monsieur,

Nous intervenons en qualité de conseil de {ac['client']}.

1. Emplacement électronique exact du contenu (art. 16, § 2, b)
{ac['url']}
[URL des republications identifiées par la veille : à compléter]

2. Explication motivée de l’illicéité (art. 16, § 2, a)
Le contenu en cause consiste en ce qui suit : {ac['faits']}
Il est manifestement illicite au regard du droit français en ce qu’il caractérise : {qual}

3. Identité du notifiant (art. 16, § 2, c)
{avocat}, avocat au Barreau de Paris, agissant pour le compte de {ac['client']} – [adresse électronique].

4. Déclaration de bonne foi (art. 16, § 2, d)
Nous confirmons, de bonne foi, que les informations et allégations contenues dans la présente notification sont exactes et complètes.

Conformément à l’article 16, § 3, du DSA, la présente notification vous confère la connaissance effective de l’illicéité du contenu au sens de l’article 6 du même règlement.

En conséquence, nous vous demandons :
– de retirer ou de rendre inaccessible ce contenu sans délai et d’empêcher sa remise en ligne ;
– de conserver les données de nature à permettre l’identification de son auteur, conformément à l’article 6 de la LCEN et au décret n° 2021-1362 du 20 octobre 2021 ;
– de nous notifier votre décision motivée (art. 16, § 5, DSA).

À défaut de retrait dans un délai de [24/48] heures, notre client se réserve le droit de saisir le juge des référés.

Éléments de preuve :
{preuve(ac)}

{avocat}
"""

    if code == "MED":
        dest = auteur if ac["auteur_connu"] else f"[Entité responsable du service] – {ac['plateforme']}"
        mineur = ("\n[Auteur mineur : adresser la présente à ses représentants légaux, civilement responsables (art. 1242 al. 4 C. civ.)]\n"
                  if ac["mineur"] else "")
        return h + f"""LETTRE RECOMMANDÉE AVEC ACCUSÉ DE RÉCEPTION + COURRIEL
Destinataire : {dest}{mineur}

Objet : Mise en demeure – retrait de contenus illicites

Madame, Monsieur,

Nous sommes le conseil de {ac['client']}.

Le contenu publié à l’adresse {ac['url']} présente les caractéristiques suivantes : {ac['faits']}

Ces faits caractérisent : {qual}

Nous vous mettons en demeure, dans un délai de [48] heures à compter de la réception de la présente :
– de supprimer l’ensemble des contenus litigieux, y compris leurs republications ;
– de vous abstenir de toute nouvelle publication de même nature ;
– [de publier le démenti / message rectificatif suivant : à compléter].

À défaut, nous saisirons sans autre avis le président du tribunal judiciaire statuant en référé aux fins de suppression sous astreinte, sans préjudice de toute action civile ou pénale.

[Note interne : la mise en demeure n’interrompt pas la prescription de 3 mois des délits de presse.]

Veuillez agréer, Madame, Monsieur, l’expression de nos salutations distinguées.

{avocat}
"""

    if code == "REFERE":
        art53 = ("\n[Délit de presse : l’assignation doit, à peine de nullité, préciser et qualifier le fait incriminé et indiquer le texte applicable (art. 53 L. 1881) – citer exactement les propos.]"
                 if presse and not fondement_civil else "")
        ident = ("\n– ORDONNER à la défenderesse de communiquer les données d’identification de l’auteur des contenus, dans un délai de [8] jours ;"
                 if not ac["auteur_connu"] else "")
        cite = ac["auteur_nom"] if ac["auteur_connu"] else f"[Entité responsable de {ac['plateforme']} – dénomination, forme, siège]"
        return h + f"""ASSIGNATION EN RÉFÉRÉ [D’HEURE À HEURE – art. 485 al. 2 CPC, sur autorisation du président]

L’an deux mille vingt-six et le [__]

À LA REQUÊTE DE : {ac['client']} [état civil ou forme sociale et siège – art. 54 et 648 CPC]
Ayant pour avocat le Cabinet REPLIK, {avocat}, avocat au Barreau de Paris

J’AI, commissaire de justice soussigné, DONNÉ ASSIGNATION À : {cite}

D’AVOIR À COMPARAÎTRE devant le président du tribunal judiciaire de Paris, statuant en référé, à l’audience du [date] à [heure].

PLAISE AU PRÉSIDENT

I. FAITS
{ac['faits']}
Contenu accessible à l’adresse {ac['url']}, constaté le {ac['timestamp']}.
Notification DSA adressée le [date], restée sans effet.

II. DISCUSSION
A. Compétence
Compétence internationale : art. 7, 2) du règlement (UE) n° 1215/2012 (centre des intérêts de la victime – CJUE, 25 oct. 2011, eDate Advertising, C-509/09 et C-161/10). Compétence territoriale : art. 46 CPC.

B. Trouble manifestement illicite et dommage imminent (art. 835 al. 1 CPC)
Les faits caractérisent : {qual}{art53}
[Alternative à arbitrer : procédure accélérée au fond prévue par la LCEN – vérifier la référence en vigueur.]

C. Mesures sollicitées
Seule la suppression rapide des contenus est de nature à faire cesser le trouble, compte tenu de leur viralité.

PAR CES MOTIFS
– ORDONNER la suppression des contenus accessibles à l’adresse {ac['url']} et de leurs reproductions, sous astreinte de [__] € par jour de retard à compter de [24 heures] suivant la signification de l’ordonnance ;{ident}
– CONDAMNER la défenderesse à verser à {ac['client']} une provision de [__] € (art. 835 al. 2 CPC) ;
– CONDAMNER la défenderesse au paiement de [__] € au titre de l’article 700 CPC, ainsi qu’aux dépens.

PIÈCES
{preuve(ac)}
– Notification DSA et justificatif d’envoi [à joindre]
"""

    if code == "REQ145":
        return h + f"""REQUÊTE AUX FINS DE COMMUNICATION DE DONNÉES D’IDENTIFICATION
(art. 145 et 493 et s. CPC)

À Monsieur ou Madame le président du tribunal judiciaire de Paris

REQUÉRANT : {ac['client']} [état civil ou forme sociale]
Ayant pour avocat : Cabinet REPLIK, {avocat}

1. Faits
{ac['faits']} – contenu accessible à l’adresse {ac['url']} ({ac['plateforme']}), publié par un compte anonyme ou pseudonyme.

2. Motif légitime (art. 145 CPC)
L’identification de l’auteur est le préalable nécessaire à l’action envisagée ({JUSTICE[ac['justice']]}), les faits caractérisant : {qual}

3. Dérogation au principe de la contradiction (art. 493 CPC)
Le risque de dépérissement des données et d’alerte de l’auteur, susceptible de supprimer ses comptes, justifie qu’il soit statué non contradictoirement.

4. Mesure sollicitée
ORDONNER à [entité responsable de {ac['plateforme']}] de communiquer au requérant, dans un délai de [8] jours, les données d’identification du titulaire du compte, conservées en application de l’article 6 de la LCEN et du décret n° 2021-1362 du 20 octobre 2021 [périmètre à vérifier : identité civile et données de compte ; adresses IP soumises au régime restrictif de l’art. L. 34-1 CPCE].

PIÈCES
{preuve(ac)}

{avocat}
"""

    if code == "PLAINTE":
        avert = ("\n[ATTENTION – délit de presse : la plainte simple n’interrompt pas la prescription de 3 mois (art. 65 L. 1881). Privilégier la citation directe ou la plainte avec constitution de partie civile.]\n"
                 if presse else "")
        contre = ac["auteur_nom"] if ac["auteur_connu"] else "X"
        return h + f"""LETTRE RECOMMANDÉE AVEC ACCUSÉ DE RÉCEPTION
Monsieur ou Madame le procureur de la République
près le tribunal judiciaire de [Paris]
[Pôle national de lutte contre la haine en ligne, le cas échéant]
{avert}
Objet : Plainte contre {contre}

Monsieur ou Madame le procureur de la République,

Je vous saisis, en qualité de conseil de {ac['client']}, d’une plainte contre {contre} des chefs de :
{qual}

I. Exposé des faits
{ac['faits']}
Contenu diffusé sur {ac['plateforme']}, à l’adresse {ac['url']}, depuis le [date de première mise en ligne].

II. Préjudice
[Préjudice moral, atteinte à la réputation, retentissement personnel et professionnel : à compléter avec le client.]

III. Actes sollicités
– Réquisitions aux plateformes concernées aux fins d’identification de l’auteur (art. 77-1-1 CPP) ;
– Conservation et saisie des données de connexion ;
– [Toute mesure de protection utile de la victime.]

Mon client entend se constituer partie civile et sera tenu informé des suites réservées à la présente plainte.

PIÈCES
{preuve(ac)}

Je vous prie d’agréer, Monsieur ou Madame le procureur de la République, l’expression de ma haute considération.

{avocat}
"""

    if code == "CITATION":
        p53 = ("""
[Délit de presse – formalisme à peine de nullité (art. 53 L. 1881) :
– reproduire exactement chaque propos poursuivi et en préciser la qualification (diffamation OU injure, sans cumul pour un même propos) ;
– viser le texte de la peine applicable (art. 32 ou 33) ;
– élire domicile dans la ville du siège de la juridiction ;
– notifier la citation au ministère public ;
– délai de 20 jours entre la citation et la comparution (art. 54) ; le prévenu dispose de 10 jours pour offrir la preuve (art. 55).]
""" if presse else "")
        return h + f"""CITATION DIRECTE DEVANT LE TRIBUNAL CORRECTIONNEL DE PARIS
(art. 390 et s. et 550 et s. CPP)
{p53}
À LA REQUÊTE DE : {ac['client']}, partie civile, élisant domicile au Cabinet REPLIK
J’AI, commissaire de justice soussigné, DONNÉ CITATION À : {ac['auteur_nom']}

D’AVOIR À COMPARAÎTRE devant la [__] chambre du tribunal correctionnel de Paris, le [date] à [heure].

I. Faits
{ac['faits']} – {ac['url']}
[Propos exacts poursuivis : à reproduire entre guillemets]

II. Qualification
Les faits sont constitutifs de : {qual}

III. Demandes
– DÉCLARER le prévenu coupable des faits visés ;
– RECEVOIR {ac['client']} en sa constitution de partie civile ;
– CONDAMNER le prévenu à lui verser [__] € de dommages-intérêts et [__] € au titre de l’article 475-1 CPP ;
– [ORDONNER la suppression des contenus et la publication du jugement.]

[Consignation fixée par le tribunal (art. 392-1 CPP) – non incluse dans le forfait.]

PIÈCES
{preuve(ac)}
"""

    if code == "CPC":
        p = ("\n[Délit de presse : dispense de plainte préalable au procureur (art. 85 al. 2 CPP). La plainte doit articuler et qualifier les faits ; consigner dans le délai fixé (art. 88 CPP) pour préserver l’interruption de la prescription.]\n"
             if presse else "\n[Justifier d’une plainte préalable restée sans suite ou d’un délai de 3 mois écoulé (art. 85 al. 2 CPP).]\n")
        return h + f"""PLAINTE AVEC CONSTITUTION DE PARTIE CIVILE (art. 85 CPP)

Monsieur ou Madame le doyen des juges d’instruction
du tribunal judiciaire de Paris
{p}
{ac['client']}, ayant pour avocat le Cabinet REPLIK, déclare porter plainte et se constituer partie civile contre {auteur} des chefs de :
{qual}

I. Faits
{ac['faits']} – {ac['url']} ({ac['plateforme']})
[Propos exacts poursuivis : à reproduire entre guillemets]

II. Préjudice
[À compléter]

III. Actes sollicités
[Audition, réquisitions, identification : à compléter]

PIÈCES
{preuve(ac)}

{avocat}
"""
    return h


def vigilance(ac):
    pts = ["J’ai vérifié la qualification proposée par l’IA locale au regard des faits et des pièces.",
           "J’ai vérifié l’identité du client et l’absence de conflit d’intérêts.",
           "J’ai relu et adapté l’acte ; il ne promet aucun résultat (obligation de moyens)."]
    if ac["regime"] in ("presse", "mixte"):
        pts.append("Loi de 1881 : faits articulés et qualifiés, texte de la peine visé (art. 53), sans cumul de qualifications.")
        pts.append("Pas de requalification d’un abus de la liberté d’expression sur l’art. 1240 C. civ. (Ass. plén., 12 juill. 2000).")
    if not ac["auteur_connu"]:
        pts.append("Auteur anonyme : demande de conservation des données d’identification incluse.")
    if ac["mineur"]:
        pts.append("Mineur concerné : action par les représentants légaux, priorité au retrait.")
    if ac["discretion"]:
        pts.append("Stratégie de discrétion (anti-effet Streisand) validée avec le client.")
    return pts


# ==============================================================================
# EN-TÊTE
# ==============================================================================
st.markdown("""
<div class="replik-header">
  <span class="badge-role">CABINET D’AVOCATS – DROIT DU NUMÉRIQUE ET DE LA RÉPUTATION · PROTOTYPE BÊTA</span>
  <h1 style="margin:8px 0 4px 0; color:white;">CABINET REPLIK – Plus vite que la viralité.</h1>
  <p style="margin:0; opacity:0.9; font-size:1.02em;">L’IA détecte et prépare. L’avocat décide et agit.</p>
</div>
""", unsafe_allow_html=True)

tab_client, tab_avocat, tab_test = st.tabs([
    "👤 Espace client – signaler et suivre",
    "⚖️ Poste avocat – valider et signer",
    "🧪 Banc d’essai – 10 faux signalements",
])


def kpi(col, label, valeur, sous="", ton=""):
    col.markdown(f"<div class='kpi {('kpi-' + ton) if ton else ''}'><div class='kpi-label'>{label}</div>"
                 f"<div class='kpi-value'>{valeur}</div><div class='kpi-sub'>{sous}</div></div>",
                 unsafe_allow_html=True)


# ==============================================================================
# ESPACE CLIENT – les 3 écrans des slides : formulaire, accusé horodaté, suivi
# ==============================================================================
def soumettre(preset, k):
    s = st.session_state
    faits = s[f"faits_{k}"]
    if faits.strip() == preset["faits"].strip():
        qual, reg = preset["ia_qualification"], preset["regime"]
        ia_act, arb, just, actes = preset["ia_actions"], preset["avocat_arbitrage"], preset["justice"], preset["actes"]
    else:
        qual, reg = qualifier(faits)
        ia_act = "Qualification provisoire par l’IA locale (simulation), empreinte SHA-256 des pièces, préparation de la notification DSA."
        arb = "Confirmer ou corriger la qualification, choisir la voie procédurale et l’acte à émettre."
        auteur = s[f"auteur_{k}"]
        just = "J2A" if auteur else ("J2C" if reg == "presse" else "J2B")
        actes = ["DSA", "MED", "REFERE"] + (["CITATION"] if auteur else ["REQ145", "PLAINTE"])
    pieces = []
    for f in (s.get(f"pieces_{k}") or []):
        pieces.append({"nom": f.name, "sha": hashlib.sha256(f.getvalue()).hexdigest()})
    s.compteur += 1
    profil = s[f"profil_{k}"]
    s.active_case = ouvrir_dossier(preset, **{
        "id": f"RPK-2026-{s.compteur}",
        "client": s[f"client_{k}"], "profil": profil,
        "niveau": s.get(f"niveau_{k}") if profil in ABONNEMENTS else None,
        "formule": s[f"formule_{k}"], "plateforme": s[f"plat_{k}"], "url": s[f"url_{k}"],
        "jours_pub": max(0, (datetime.date.today() - s[f"date_{k}"]).days),
        "auteur_connu": s[f"auteur_{k}"], "auteur_nom": s.get(f"auteur_nom_{k}", "") if s[f"auteur_{k}"] else "",
        "urgence_nuit": s[f"nuit_{k}"], "discretion": s[f"discret_{k}"], "faits": faits,
        "ia_qualification": qual, "regime": reg, "ia_actions": ia_act, "avocat_arbitrage": arb,
        "justice": just, "actes": actes, "pieces": pieces,
    })
    s.flash_client = True


with tab_client:
    st.selectbox("⚡ Remplissage rapide – choisir un cas type pour la démonstration",
                 LABELS, key="preset_label")
    preset = PAR_LABEL[st.session_state.preset_label]
    k = preset["id"]  # les champs se réinitialisent quand on change de cas type

    col_form, col_suivi = st.columns([1.1, 1], gap="large")

    # ---------- ÉCRAN 1 : FORMULAIRE ----------
    with col_form:
        st.markdown("#### ① Signaler une atteinte")
        st.caption("Formulaire simple : un avocat de permanence prend le relais 24h/24, 7j/7.")

        c1, c2 = st.columns(2)
        c1.text_input("Nom ou raison sociale", value=preset["client"], key=f"client_{k}")
        codes_profils = list(PROFILS.keys())
        profil = c2.selectbox("Votre situation", codes_profils, format_func=lambda c: PROFILS[c],
                              index=codes_profils.index(preset["profil"]), key=f"profil_{k}")
        niveau = None
        if profil in ABONNEMENTS:
            niveau = st.radio("Niveau de votre abonnement", [1, 2, 3], horizontal=True,
                              format_func=lambda n: f"{NIVEAUX[n]} ({ABONNEMENTS[profil][n]} € HT / mois)",
                              index=(preset["niveau"] or 1) - 1, key=f"niveau_{k}")

        c3, c4 = st.columns([1.4, 1])
        c3.text_input("Plateforme ou site concerné", value=preset["plateforme"], key=f"plat_{k}")
        c4.date_input("Date de première mise en ligne", format="DD/MM/YYYY",
                      value=datetime.date.today() - datetime.timedelta(days=preset["jours_pub"]), key=f"date_{k}")
        st.text_input("Lien (URL) exact du contenu", value=preset["url"], key=f"url_{k}")
        st.text_area("Que se passe-t-il ? Décrivez le contenu ou collez le message reçu",
                     value=preset["faits"], height=100, key=f"faits_{k}",
                     help="Si vous modifiez ce texte, l’IA locale (simulée) propose une nouvelle qualification.")
        st.file_uploader("Captures d’écran, photos, vidéos – une empreinte SHA-256 est calculée dès l’envoi",
                         type=["png", "jpg", "jpeg", "mp4", "pdf"], accept_multiple_files=True, key=f"pieces_{k}")

        st.markdown("##### Votre formule (prix connu d’avance, frais de tiers inclus)")
        codes_f = list(FORMULES.keys())
        formule = st.radio("Formule Réaction", codes_f, format_func=lambda c: FORMULES[c],
                           index=codes_f.index(preset["formule"]), key=f"formule_{k}", label_visibility="collapsed")

        auteur = st.checkbox("Je connais l’identité de l’auteur", value=preset["auteur_connu"], key=f"auteur_{k}")
        if auteur:
            st.text_input("Nom de l’auteur (si vous le connaissez)", value=preset["auteur_nom"], key=f"auteur_nom_{k}")
        nuit = st.checkbox("Intervention urgente de nuit, le week-end ou un jour férié",
                           value=preset["urgence_nuit"], key=f"nuit_{k}",
                           help="Majoration affichée : +75 € HT (R1, R2) · +150 € HT (R3) · +20 € HT par intervention pour les abonnés.")
        st.checkbox("Je souhaite une démarche discrète (aucun contact avec l’auteur sans mon accord)",
                    value=preset["discretion"], key=f"discret_{k}")

        lo, hi, detail, majo = calcul_devis(profil, niveau, formule, nuit)
        majo_txt = f" · dont majoration nuit / week-end : {eur(majo)} HT" if majo else ""
        st.markdown(f"""<div class="devis"><div class="kpi-label">Votre prix, connu d’avance</div>
            <div class="devis-prix">{libelle_prix(lo, hi)}</div>
            <div class="kpi-sub">{detail}{majo_txt}. Aucune démarche sans validation d’un avocat. Nous promettons des moyens, jamais un résultat.</div></div>""",
                    unsafe_allow_html=True)
        st.write("")
        st.button("🛡️ ENVOYER MON SIGNALEMENT ET RECEVOIR MON ACCUSÉ HORODATÉ", type="primary",
                  width="stretch", on_click=soumettre, args=(preset, k))

    # ---------- ÉCRANS 2 ET 3 : ACCUSÉ HORODATÉ & SUIVI ----------
    with col_suivi:
        ac = st.session_state.active_case
        if st.session_state.pop("flash_client", False):
            st.success("✅ Signalement reçu. Votre accusé horodaté est disponible ci-dessous ; l’avocat de permanence est alerté.")

        st.markdown("#### ② Votre accusé de réception horodaté")
        niveau_preuve = {
            "R1": "Accusé de signalement (n’établit pas à lui seul l’existence du contenu en ligne)",
            "R2": "Capture certifiée horodatée en cours",
            "R3": "Constat de commissaire de justice d’astreinte – commissaire saisi",
            "R4": "Constat de commissaire de justice préalable au référé",
        }[ac["formule"]]
        pieces_html = "".join(f"<b>PIÈCE :</b> {p['nom']}<br>SHA-256 : {p['sha']}<br>" for p in ac["pieces"])
        st.markdown(f"""<div class="cert-box">
            <b>🛡️ ACCUSÉ DE RÉCEPTION HORODATÉ – CABINET REPLIK</b><br>
            ----------------------------------------------------<br>
            <b>DOSSIER :</b> {ac['id']} | <b>CLIENT :</b> {ac['client']}<br>
            <b>SIGNALEMENT REÇU LE :</b> {ac['timestamp']}<br>
            <b>URL SIGNALÉE :</b> {ac['url']}<br>
            <b>EMPREINTE DU SIGNALEMENT (SHA-256) :</b><br>{ac['sha256']}<br>
            {pieces_html}
            <b>NIVEAU DE PREUVE :</b> {niveau_preuve}<br>
            <b>CONSERVATION :</b> hébergement en France – 5 ans, suppression sur simple demande
        </div>""", unsafe_allow_html=True)
        st.caption("L’empreinte SHA-256 permet de démontrer que les pièces n’ont pas été modifiées depuis leur réception. "
                   "La preuve de l’existence du contenu en ligne relève de la capture certifiée (R2) ou du constat de commissaire de justice (R3).")
        accuse_txt = (f"ACCUSÉ DE RÉCEPTION HORODATÉ – CABINET REPLIK\nDossier : {ac['id']}\nClient : {ac['client']}\n"
                      f"Reçu le : {ac['timestamp']}\nURL : {ac['url']}\nSHA-256 : {ac['sha256']}\n"
                      + "".join(f"Pièce {p['nom']} – SHA-256 : {p['sha']}\n" for p in ac["pieces"])
                      + f"Niveau de preuve : {niveau_preuve}\n")
        st.download_button("📥 Télécharger mon accusé", data=accuse_txt, file_name=f"Accuse_{ac['id']}.txt", width="stretch")

        st.markdown("#### ③ Suivi de votre dossier")
        signe = ac["statut"] == "signe"
        etapes = [
            ("01 Détection", "IA", "done", "Contenu et URL enregistrés"),
            ("02 Qualification", "IA", "done", "Préparée par l’IA locale"),
            ("03 Validation", "AVOCAT", "done" if signe else "active", "Validée par l’avocat" if signe else "⏳ Avocat de permanence saisi"),
            ("04 Action", "AVOCAT", "done" if signe else "wait", "🚀 Démarche engagée" if signe else "En attente de signature"),
            ("05 Suivi", "CLIENT", "active" if signe else "wait", "🛡️ Veille 7 jours active" if signe else "Après l’action"),
        ]
        cols = st.columns(5)
        for c, (titre, acteur, etat, txt) in zip(cols, etapes):
            c.markdown(f"<div class='step step-{etat}'><div class='step-actor'>{acteur}</div><b>{titre}</b><br><small>{txt}</small></div>",
                       unsafe_allow_html=True)
        st.write("")
        if signe:
            st.success(f"⚖️ **Message de votre avocat ({ac['avocat_signataire']}) :** votre dossier a été validé et la démarche suivante a été engagée : **{ACTES[ac['acte_code']]}**.")
            st.download_button("📥 Télécharger la copie de l’acte", data=ac["acte_final"],
                               file_name=f"Copie_client_{ac['id']}.txt", width="stretch")
        else:
            st.info("👨‍⚖️ **Prochaine étape :** l’avocat de permanence examine votre dossier dans les prochaines minutes. Aucune démarche n’est engagée sans son contrôle et sa signature.")

        with st.expander("🧭 En attendant : les bons réflexes", expanded=not signe):
            reflexes = ["Ne supprimez pas vos comptes ni les messages : ce sont vos preuves.",
                        "Ne contactez pas l’auteur et ne répondez pas publiquement.",
                        "Notez les autres liens où le contenu réapparaît et transmettez-les-nous."]
            if "312-10" in ac["ia_qualification"] or "Chantage" in ac["ia_qualification"]:
                reflexes.insert(0, "**Ne payez pas** : le paiement n’arrête presque jamais le chantage.")
            if "223-1-1" in ac["ia_qualification"]:
                reflexes.insert(0, "**En cas de danger immédiat, appelez le 17.**")
            st.markdown("\n".join(f"- {r}" for r in reflexes))
            st.caption("Besoin de parler à quelqu’un ? 3018 (victimes de cyberharcèlement, gratuit) · 3114 (détresse, 24h/24).")

        st.markdown("##### 🔍 Veille anti-republication (1 semaine, dès R1)")
        st.dataframe(pd.DataFrame([
            {"Cible surveillée": ac["plateforme"], "État": "Retrait demandé" if signe else "Preuve conservée", "Republications": "0 détectée"},
            {"Cible surveillée": "Moteurs de recherche et réseaux", "État": "Surveillance continue", "Republications": "0 détectée"},
        ]), width="stretch", hide_index=True)

# ==============================================================================
# POSTE AVOCAT – contrôle humain et signature
# ==============================================================================
def signer(ac_id, code, avocat, cle_draft, cle_notes):
    s = st.session_state
    if s.active_case["id"] != ac_id:
        return
    s.active_case.update({
        "statut": "signe", "avocat_signataire": avocat, "acte_code": code,
        "acte_final": s[cle_draft], "notes_internes": s.get(cle_notes, ""),
    })
    s.flash_avocat = True


with tab_avocat:
    ac = st.session_state.active_case
    st.subheader(f"⚖️ Dossier {ac['id']} – {ac['client']}")
    st.caption("Interface interne. Qualification préparée par l’IA locale du cabinet, hébergée en France : aucune donnée transmise à une IA externe.")

    p = prescription(ac)
    k1, k2, k3, k4 = st.columns(4)
    kpi(k1, "Ancienneté de la publication", f"{ac['jours_pub']} jour{'s' if ac['jours_pub'] > 1 else ''}",
        "Point de départ : première mise en ligne")
    if p["court"]:
        if p["restant"] < 0:
            kpi(k2, "Prescription presse", "EXPIRÉE", f"{p['texte']} · depuis le {p['fin'].strftime('%d/%m/%Y')}", "alert")
        else:
            ton = "alert" if p["restant"] <= 15 else ("warn" if p["restant"] <= 30 else "ok")
            kpi(k2, "Prescription presse", f"J-{p['restant']}", f"{p['texte']} · échéance le {p['fin'].strftime('%d/%m/%Y')}", ton)
    else:
        kpi(k2, "Prescription", p["texte"].split(" – ")[0], p["texte"].split(" – ")[1] + " · pas d’urgence de délai", "ok")
    kpi(k3, "Auteur", "Identifié" if ac["auteur_connu"] else "Anonyme ou pseudonyme",
        ac["auteur_nom"] if ac["auteur_connu"] else "Identification à obtenir", "" if ac["auteur_connu"] else "warn")
    lo, hi, detail, majo = calcul_devis(ac["profil"], ac["niveau"], ac["formule"], ac["urgence_nuit"])
    kpi(k4, "Formule et créneau", f"{ac['formule']} · {'Nuit / WE' if ac['urgence_nuit'] else 'Heures ouvrées'}",
        f"{libelle_prix(lo, hi)}" + (f" (majoration {eur(majo)})" if majo else ""), "warn" if ac["urgence_nuit"] else "")

    st.write("")
    if presse_prescrite(ac):
        st.error("🚨 **Prescription de la loi de 1881 acquise.** Les actes pénaux fondés sur la loi de 1881 sont verrouillés. "
                 "Réorientation éventuelle sur le dénigrement (art. 1240 C. civ., 5 ans) – uniquement si les propos visent des produits ou prestations.")
    elif p["court"] and p["restant"] <= 15:
        st.warning(f"⚠️ **Urgence procédurale :** {p['restant']} jours pour interrompre la prescription par un acte de poursuite (citation directe ou plainte avec constitution de partie civile).")

    st.divider()
    col_ia, col_val = st.columns([1, 1.15], gap="large")

    with col_ia:
        st.markdown("#### 1. Préparation par l’IA locale")
        st.info(f"« {ac['faits']} »\n\n🔗 `{ac['url']}`\n\n🔐 SHA-256 : `{ac['sha256'][:32]}…`")
        st.markdown("**Qualification proposée** *(à confirmer par l’avocat)*")
        st.success(f"⚖️ {ac['ia_qualification']}")
        st.markdown(f"- 🤖 **Traité par l’IA :** {ac['ia_actions']}")
        st.markdown(f"- 👨‍⚖️ **Décision renvoyée à l’avocat :** {ac['avocat_arbitrage']}")
        st.markdown(f"- 💼 **Suite Justice suggérée :** {JUSTICE[ac['justice']]}")
        st.text_area("Notes internes de l’avocat (non reproduites dans l’acte)", key=f"notes_{ac['id']}", height=90)

    with col_val:
        st.markdown("#### 2. Contrôle humain et signature")
        if st.session_state.pop("flash_avocat", False):
            st.success("✅ Acte signé. Le suivi client est passé à l’étape 04 « Action ».")

        avocats = ["Me [Nom], associé pénal et presse", "Me [Nom], associé contentieux numérique et référés"]
        avocat = st.selectbox("Avocat de permanence", avocats, key=f"avocat_{ac['id']}")

        options = []
        for code in ACTES:
            if code in ACTES_PENAUX and presse_prescrite(ac):
                continue
            if code == "CITATION" and not ac["auteur_connu"]:
                continue
            if code == "REQ145" and ac["auteur_connu"]:
                continue
            options.append(code)
        options.sort(key=lambda c: (c not in ac["actes"], list(ACTES).index(c)))
        code = st.selectbox("Acte pré-rédigé à émettre", options,
                            format_func=lambda c: ("⭐ " if c in ac["actes"] else "") + ACTES[c],
                            key=f"acte_{ac['id']}", help="⭐ = actes suggérés par l’IA pour ce dossier. Les actes incompatibles avec le dossier sont masqués.")

        cle_draft = f"draft_{ac['id']}_{code}_{avocats.index(avocat)}"
        if cle_draft not in st.session_state:
            st.session_state[cle_draft] = rediger(code, ac, avocat)
        st.text_area("Projet d’acte – modifiable ; les crochets [ ] signalent les points à compléter", key=cle_draft, height=340)
        restants = st.session_state[cle_draft].count("[")
        if restants:
            st.caption(f"✏️ {restants} passage(s) entre crochets restent à compléter ou à supprimer avant envoi.")

        st.markdown("**Points de contrôle avant signature**")
        coches = [st.checkbox(t, key=f"chk_{ac['id']}_{i}") for i, t in enumerate(vigilance(ac))]
        tout_coche = all(coches)
        st.button("✅ VALIDER, SIGNER ET NOTIFIER LE CLIENT", type="primary", width="stretch",
                  disabled=not tout_coche or ac["statut"] == "signe",
                  on_click=signer, args=(ac["id"], code, avocat, cle_draft, f"notes_{ac['id']}"))
        if not tout_coche:
            st.caption("🔒 Signature possible une fois tous les points de contrôle cochés : 100 % des démarches sont validées par un avocat.")
        st.download_button("📄 Exporter le projet (.txt)", data=st.session_state[cle_draft],
                           file_name=f"{code}_{ac['id']}.txt", width="stretch")

# ==============================================================================
# BANC D’ESSAI – mesure : ce que l’IA traite, ce qu’elle renvoie à l’avocat (slide 18)
# ==============================================================================
def charger(d):
    st.session_state.active_case = ouvrir_dossier(d)
    st.session_state.preset_label = d["label"]
    st.session_state.flash_test = d["id"]


with tab_test:
    st.subheader("🧪 Banc d’essai – 10 faux signalements")
    st.caption("Mesure : ce que l’IA traite, ce qu’elle renvoie à l’avocat.")
    flash = st.session_state.pop("flash_test", None)
    if flash:
        st.success(f"✅ Dossier {flash} ouvert : il est maintenant affiché dans l’Espace client et au Poste avocat.")

    n = len(DOSSIERS_TYPES)
    n_actes = sum(len(d["actes"]) for d in DOSSIERS_TYPES)
    n_anon = sum(not d["auteur_connu"] for d in DOSSIERS_TYPES)
    n_presse = sum(d["regime"] in ("presse", "mixte") for d in DOSSIERS_TYPES)
    n_nuit = sum(d["urgence_nuit"] for d in DOSSIERS_TYPES)
    m = st.columns(5)
    kpi(m[0], "Signalements testés", f"{n}", "Particuliers, personnalités, entreprises")
    kpi(m[1], "Actes pré-rédigés par l’IA", f"{n_actes}", "Tous soumis à validation")
    kpi(m[2], "Décisions renvoyées à l’avocat", f"{n} / {n}", "100 % des démarches validées", "ok")
    kpi(m[3], "Délai de 3 mois à surveiller", f"{n_presse}", "Dossiers relevant de la loi de 1881", "warn")
    kpi(m[4], "Auteurs à identifier", f"{n_anon}", f"dont {n_nuit} interventions de nuit / WE")

    st.write("")
    lignes = []
    for d in DOSSIERS_TYPES:
        pr = prescription(d)
        lo, hi, _, _ = calcul_devis(d["profil"], d["niveau"], d["formule"], d["urgence_nuit"])
        lignes.append({
            "Dossier": d["id"], "Situation": d["titre"],
            "Profil": d["profil"] + (f" N{d['niveau']}" if d["niveau"] else ""),
            "Prescription": ("EXPIRÉE" if pr["court"] and pr["restant"] < 0 else (f"J-{pr['restant']}" if pr["court"] else pr["texte"].split(" – ")[0])),
            "Auteur": "Identifié" if d["auteur_connu"] else "Anonyme",
            "Formule": d["formule"] + (" + nuit" if d["urgence_nuit"] else ""),
            "Prix": libelle_prix(lo, hi), "Suite Justice": d["justice"],
        })
    st.dataframe(pd.DataFrame(lignes), width="stretch", hide_index=True)

    st.markdown("#### Détail : ce que l’IA automatise, ce que l’avocat tranche")
    for d in DOSSIERS_TYPES:
        with st.expander(f"📁 {d['label']}"):
            ci, cb = st.columns([4, 1])
            ci.markdown(f"- **Faits :** {d['faits']}\n"
                        f"- **Qualification proposée :** {d['ia_qualification']}\n"
                        f"- 🤖 **IA :** {d['ia_actions']}\n"
                        f"- ⚖️ **Avocat :** {d['avocat_arbitrage']}\n"
                        f"- 📄 **Actes préparés :** {', '.join(ACTES[a] for a in d['actes'])}")
            cb.button("Ouvrir ce dossier", key=f"btn_{d['id']}", width="stretch", on_click=charger, args=(d,),
                      help="Remplace le dossier affiché dans l’Espace client et au Poste avocat.")

    with st.expander("📝 Note « usage de l’IA » – ce que la bêta simule"):
        st.markdown("""
- **Détection (étape 01)** : en production, assurée par l’IA d’un prestataire certifié hébergé en France ; ici, simulée par le signalement du client ou les cas types.
- **Qualification (étape 02)** : en production, modèle d’IA hébergé chez un opérateur français et orchestré par n8n en local ; ici, fiches pré-rédigées et règles par mots-clés (modifiez la description des faits pour le voir réagir).
- **Actes** : modèles pré-rédigés remplis automatiquement à partir du dossier ; les passages entre crochets restent à compléter par l’avocat.
- **Contrôle humain** : aucun acte n’est signé sans que l’avocat ait coché chaque point de contrôle.
- **Ce que la bêta ne fait pas** : aucun envoi réel, aucun horodatage qualifié, aucune donnée conservée après la session.
""")

# ==============================================================================
# BARRE LATÉRALE (rendue en dernier pour refléter l’état à jour)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🛡️ CABINET REPLIK")
    st.caption("La rigueur juridique, à la vitesse d’Internet.")
    st.divider()
    ac = st.session_state.active_case
    st.markdown("### ⚡ Permanence 24h/24, 7j/7")
    if ac["statut"] == "signe":
        st.success(f"🟢 **{ac['id']}** : acte signé par l’avocat.")
    else:
        st.warning(f"🟠 **{ac['id']}** : préparé par l’IA locale, en attente de validation.")
    st.divider()
    st.markdown("### 🔒 Nos engagements")
    st.markdown("""
- **24h/24** : un avocat de permanence, 7j/7.
- **0 € de frais cachés** : frais de tiers inclus.
- **100 %** des démarches validées par un avocat.
- **1 semaine** de veille anti-republication dès R1.
- **0 donnée sensible** envoyée à une IA externe.
""")
    st.caption("Nous promettons des moyens, jamais un résultat. Prototype pédagogique – LAB EFB.")
