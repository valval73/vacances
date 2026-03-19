#!/usr/bin/env python3
"""
PEA Screener Pro — Journal Financier Hebdomadaire
Envoi samedi 8h vers romence1@gmail.com
Format : vrai journal - résumé semaine narrative + données + analyses Grade A
"""
import json, urllib.request, smtplib, os, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

RECIPIENT = "romence1@gmail.com"
SENDER    = "romence1@gmail.com"
PASSWORD  = os.environ.get("GMAIL_PASSWORD", "")

INDICES = {
    "CAC 40":"^FCHI","Euro Stoxx 50":"^STOXX50E","DAX":"^GDAXI",
    "S&P 500":"^GSPC","Nasdaq 100":"^NDX","FTSE 100":"^FTSE",
    "Or $/oz":"GC=F","Petrole Brent":"BZ=F","EUR/USD":"EURUSD=X",
    "Taux US 10 ans":"^TNX","Bitcoin":"BTC-USD","VIX":"^VIX",
}

PEA_WATCHLIST = {
    "MC":("LVMH","MC.PA"),"AI":("Air Liquide","AI.PA"),"OR":("LOreal","OR.PA"),
    "RMS":("Hermes","RMS.PA"),"SAF":("Safran","SAF.PA"),"GTT":("GTT","GTT.PA"),
    "COFA":("Coface","COFA.PA"),"TTE":("TotalEnergies","TTE.PA"),
    "LR":("Legrand","LR.PA"),"DG":("Vinci","DG.PA"),"SU":("Schneider","SU.PA"),
    "BNP":("BNP Paribas","BNP.PA"),"DASSAV":("Dassault Aviation","AM.PA"),
    "ASML":("ASML","ASML.AS"),"NOVO":("Novo Nordisk","NOVO-B.CO"),
    "ALV":("Allianz","ALV.DE"),"VIRBAC":("Virbac","VIRP.PA"),
    "IPSEN":("Ipsen","IPA.PA"),"STEF":("STEF","STF.PA"),
    "INTERPARFUMS":("Interparfums","ITP.PA"),
}

# Analyses narratives Grade A - ecrites par le cabinet
GRADE_A_ANALYSES = [
    {
        "ticker":"AI","name":"Air Liquide","prix_zone":"145-162","stop":"132","obj":"178",
        "tv":"EURONEXT:AI","zb":"Air+Liquide","ms":"ai",
        "resume":(
            "Imaginez une autoroute que chaque usine chimique, chaque hopital, chaque fabricant de puces"
            " electroniques DOIT emprunter pour fonctionner. C est Air Liquide. Ses pipelines de gaz"
            " industriels (oxygene, azote, hydrogene) sont litteralement entres dans les murs des usines"
            " de ses clients - les enlever couterait plus cher que de les garder. C est ce qu on appelle"
            " un switching cost absolu. Les contrats durent 15-20 ans avec clause d indexation inflation"
            " automatique. Resultat : ROE 18% constant depuis 40 ans, dividende en hausse CHAQUE annee"
            " depuis 1956. Ce titre EST le PEA ideal - on l achete, on le garde, on touche les dividendes."
        ),
        "pdg":"Francois Jackow (depuis 2022) - ancien COO, connait l entreprise depuis 1992. Execution"
              " parfaite, pas de surprises. Track record direction 100%.",
        "catalyseur":"Hydrogene vert (35 projets 2026-2030) + semi-conducteurs ultra-purs (boom IA). +20% upside DCF.",
    },
    {
        "ticker":"GTT","name":"GTT Gaztransport","prix_zone":"188-218","stop":"168","obj":"265",
        "tv":"EURONEXT:GTT","zb":"GTT+Gaztransport","ms":"gtt",
        "resume":(
            "GTT c est Hermes sur les mers. L entreprise possede les brevets des membranes cryogeniques"
            " qui equipent 90% des methaniers mondiaux - ces enormes navires qui transportent le gaz"
            " naturel liquefie (GNL) a -163 degres. Personne d autre ne peut faire ce que fait GTT."
            " Zero dette, ROE 85%, marge nette 58% - des chiffres de logiciel pur dans une entreprise"
            " industrielle. Le GNL remplace massivement le charbon et le petrole en Asie. 850 navires"
            " commandes pour 2026-2030. Chaque navire paie GTT pendant 30 ans en royalties."
        ),
        "pdg":"Philippe Berterottiere - fondateur de fait de la strategie actuelle. Aligne avec les actionnaires.",
        "catalyseur":"Carnet de commandes record 45 navires/an, expansion H2/NH3. RSI 45 = zone d accumulation.",
    },
    {
        "ticker":"SAF","name":"Safran","prix_zone":"225-255","stop":"200","obj":"310",
        "tv":"EURONEXT:SAF","zb":"Safran","ms":"saf",
        "resume":(
            "Quand un avion Airbus A320 ou Boeing 737 decole, il y a 95% de chances que son moteur"
            " soit le LEAP de Safran (co-fabrique avec GE). Ce moteur est vendu presque a prix coutant"
            " - c est le rasoir. Mais les 30 ans de maintenance (lames) generent des milliards de"
            " revenus recurrents a tres haute marge. La flotte mondiale va doubler d ici 2040."
            " Chaque nouvel avion livre aujourd hui garantit 30 ans de revenus a Safran. Piotroski 8/9,"
            " direction qui tient TOUTES ses guidances depuis 5 ans (track record 100%)."
        ),
        "pdg":"Olivier Andries - excellent executant. A pris les renes en 2021 et execute parfaitement"
              " le plan de montee en cadence LEAP. Achat d actions propres regulier = alignment parfait.",
        "catalyseur":"Cadence Airbus 75/mois en 2026, MRO LEAP a maturite (+25% revenus), programme RISE.",
    },
    {
        "ticker":"ASML","name":"ASML","prix_zone":"580-660","stop":"540","obj":"780",
        "tv":"NASDAQ:ASML","zb":"ASML","ms":"asml",
        "resume":(
            "ASML fabrique les seules machines au monde capables de graver des puces electroniques"
            " en dessous de 7 nanometres (EUV). TSMC, Samsung, Intel ne peuvent PHYSIQUEMENT pas"
            " produire des puces d intelligence artificielle sans ASML. Une seule machine vaut 200M$."
            " Zero concurrence possible avant 15 ans minimum. La correction de -30% depuis le pic"
            " est une opportunite historique - les commandes repartent fort. Eligible PEA via AEX Amsterdam."
        ),
        "pdg":"Christophe Fouquet (depuis 2024) - ex-EVP EUV, connait le produit mieux que quiconque.",
        "catalyseur":"Reprise commandes TSMC (IA chips 2026), EUV High-NA deploiement, expansion US.",
    },
]

def fetch_yahoo(ticker):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker + "?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta = data["chart"]["result"][0]["meta"]
        price = round(meta.get("regularMarketPrice",0),2)
        prev = meta.get("previousClose",price)
        week = meta.get("chartPreviousClose",price)
        return {"price":price,"chg_day":round((price-prev)/prev*100,2) if prev else 0,
                "chg_week":round((price-week)/week*100,2) if week else 0}
    except Exception as e:
        print("Yahoo err "+ticker+": "+str(e))
        return None

def fetch_news(url, base=""):
    arts = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept-Language":"fr-FR,fr;q=0.9"})
        html = urllib.request.urlopen(req, timeout=14).read().decode("utf-8","ignore")
        for link, title in re.findall(r'href="([^"]{10,200})"[^>]*>(?:<[^>]+>)*([^<]{30,200})', html):
            t = re.sub(r"\s+"," ",title).strip()
            if len(t)>=30 and "cookie" not in t.lower():
                fu = (base+link) if link.startswith("/") else link
                if fu not in [u for u,_ in arts]:
                    arts.append((fu,t))
            if len(arts)>=6: break
    except Exception as e:
        print("News err "+str(e))
    return arts[:5]

def arrow(chg):
    if chg is None: return '<span style="color:#888">--</span>'
    col="#22c55e" if chg>0 else "#ef4444" if chg<-0.05 else "#888"
    sign="+" if chg>0 else ""
    arr="&#9650;" if chg>0.2 else "&#9660;" if chg<-0.2 else "&#9670;"
    return '<span style="color:'+col+';font-weight:700">'+arr+" "+sign+str(chg)+'%</span>'

def pf(p):
    return "{:,.0f}".format(p) if p>1000 else "{:.4f}".format(p) if p<2 else "{:.2f}".format(p)

def interpret_market(markets):
    """Genere un resume narratif des marches de la semaine"""
    cac = markets.get("CAC 40",{})
    sp = markets.get("S&P 500",{})
    vix = markets.get("VIX",{})
    
    cac_chg = cac.get("chg_week",0) if cac else 0
    sp_chg = sp.get("chg_week",0) if sp else 0
    vix_p = vix.get("price",20) if vix else 20
    
    # Narrative
    if cac_chg > 2 and sp_chg > 2:
        humeur = "Excellente semaine pour les marches mondiaux."
        detail = "La hausse generale reflète un optimisme sur les resultats d entreprises et une inflation qui se calme."
    elif cac_chg > 0 and sp_chg > 0:
        humeur = "Semaine positive mais sans conviction."
        detail = "Les marches progressent dans un volume faible. Attendre une confirmation avant d agir."
    elif cac_chg < -2 or sp_chg < -2:
        humeur = "Semaine difficile pour les marches."
        detail = "Les baisses creent des opportunites d achat sur les actions de qualite en zone achat."
    else:
        humeur = "Semaine de consolidation sans tendance claire."
        detail = "Les investisseurs attendent les prochains chiffres macro avant de se positionner."
    
    if vix_p > 25:
        detail += " Le VIX a " + str(round(vix_p,1)) + " signale de la peur sur les marches - historiquement un bon point d entree a long terme."
    elif vix_p < 15:
        detail += " Le VIX bas a " + str(round(vix_p,1)) + " indique de la complacence - etre prudent sur les nouveaux achats."
    
    return humeur + " " + detail

def build_grade_a_section():
    """Analyses approfondies Grade A - narratif accessible"""
    parts = []
    for a in GRADE_A_ANALYSES:
        t = a["ticker"]
        n = a["name"]
        pz = a["prix_zone"]
        st = a["stop"]
        ob = a["obj"]
        tv = a["tv"]
        zb = a["zb"]
        rs = a["resume"]
        pdg = a["pdg"]
        cat = a["catalyseur"]
        
        block = (
            "<div style=\"background:#fff;border:1px solid #e8e0d5;border-radius:5px;margin-bottom:14px;overflow:hidden\">"
            "<div style=\"background:linear-gradient(90deg,#0f2540,#1a3a5c);padding:10px 16px;display:flex;justify-content:space-between;align-items:center\">"
            "<b style=\"color:#f0d080;font-family:monospace;font-size:13px\">" + t + " &mdash; " + n + "</b>"
            "<span style=\"background:#22c55e;color:#fff;font-family:monospace;font-size:8px;padding:3px 8px;border-radius:3px;font-weight:700\">GRADE A &mdash; PEPITE</span>"
            "</div>"
            "<div style=\"background:#f8fdf9;padding:8px 16px;border-bottom:1px solid #eee;font-size:11px;font-family:monospace\">"
            "<span style=\"color:#16a34a\">Zone achat : " + pz + "&#8364;</span>"
            " &nbsp;|&nbsp; <span style=\"color:#dc2626\">Stop : " + st + "&#8364;</span>"
            " &nbsp;|&nbsp; <span style=\"color:#1d4ed8\">Objectif : " + ob + "&#8364;</span>"
            "</div>"
            "<div style=\"padding:12px 16px;font-size:12px;line-height:1.8;color:#1a1a1a\">"
            "<div style=\"font-family:monospace;font-size:9px;color:#b8860b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px\">Pourquoi investir ?</div>"
            + rs +
            "</div>"
            "<div style=\"padding:8px 16px 10px;font-size:11px;color:#555;background:#fafaf8\">"
            "<span style=\"font-family:monospace;font-size:9px;color:#888;text-transform:uppercase\">Management : </span>" + pdg +
            "</div>"
            "<div style=\"padding:8px 16px;font-size:11px;color:#1a3a5c;background:#f0f4ff;border-top:1px solid #dde7ff\">"
            "<span style=\"font-family:monospace;font-size:9px;color:#1d4ed8;text-transform:uppercase;font-weight:700\">Catalyseur 2026 : </span>" + cat +
            "</div>"
            "<div style=\"padding:8px 16px 10px;display:flex;gap:6px\">"
            "<a href=\"https://fr.tradingview.com/chart/?symbol=" + tv + "&interval=W\" target=\"_blank\" style=\"padding:4px 10px;background:#b8860b;color:#fff;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px\">TradingView</a>"
            "<a href=\"https://www.zonebourse.com/recherche/?q=" + zb + "\" target=\"_blank\" style=\"padding:4px 10px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px\">Zone Bourse</a>"
            "<a href=\"https://valval73.github.io/vacances/\" target=\"_blank\" style=\"padding:4px 10px;background:#0f2540;color:#f0d080;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px\">Screener</a>"
            "</div>"
            "</div>"
        )
        parts.append(block)
    return "\n".join(parts)

def build_html(markets, pea, art_yahoo, art_bourso, art_zb):
    now = datetime.now()
    w_label = (now-timedelta(days=6)).strftime("%d/%m")+" au "+now.strftime("%d/%m/%Y")
    
    # Interpretation narrative des marches
    market_resume = interpret_market(markets)
    
    # Marchés rows
    mrows=""
    for name,d in markets.items():
        if not d: continue
        p=d["price"]
        mrows+=('<tr><td style="padding:7px 14px;border-bottom:1px solid #eee;font-size:13px">'+name+"</td>"
               +'<td style="padding:7px 14px;border-bottom:1px solid #eee;text-align:right;font-family:monospace;font-size:13px">'+pf(p)+"</td>"
               +'<td style="padding:7px 14px;border-bottom:1px solid #eee;text-align:right;font-size:13px">'+arrow(d.get("chg_week"))+"</td></tr>")
    
    # PEA perf
    sorted_pea=sorted(pea.items(),key=lambda x:x[1].get("chg_week",0),reverse=True)
    def prow(t,d):
        return ('<tr><td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;font-size:12px"><b style="font-family:monospace;color:#0f2540">'+t+'</b> <span style="color:#888;font-size:11px">'+d.get("name","")+'</span></td><td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;font-family:monospace;font-size:12px;text-align:right">'+"{:.2f}".format(d["price"])+"&#8364;</td>"+'<td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;text-align:right;font-size:12px">'+arrow(d.get("chg_week"))+"</td></tr>")
    top_rows="".join(prow(t,d) for t,d in sorted_pea[:5])
    bot_rows="".join(prow(t,d) for t,d in sorted_pea[-5:])
    
    def art_block(arts):
        if not arts: return '<p style="color:#888;font-size:12px;font-style:italic">Indisponible</p>'
        return "".join('<div style="padding:7px 0;border-bottom:1px solid #f0f0f0"><a href="'+u+'" target="_blank" style="color:#1a3a5c;text-decoration:none;font-size:12px;line-height:1.5">&#8594; '+t+"</a></div>" for u,t in arts)
    
    themes_html=(
        '<div style="background:#fff;border-left:3px solid #1d4ed8;padding:11px 14px;margin-bottom:10px">'+
        '<div style="display:flex;justify-content:space-between;margin-bottom:4px"><b style="font-size:13px">&#127968; Banques &amp; Taux BCE</b><span style="font-size:10px;color:#1d4ed8;font-weight:700;font-family:monospace">SURVEILLER</span></div>'+
        '<p style="margin:0;font-size:12px;color:#444;line-height:1.5">Tout discours Lagarde est un catalyseur pour BNP, ACA, GLE. Les taux hauts compressent les valeurs immobilieres mais beneficient aux banques (NIM eleve).</p></div>'+
        '<div style="background:#fff;border-left:3px solid #16a34a;padding:11px 14px;margin-bottom:10px">'+
        '<div style="display:flex;justify-content:space-between;margin-bottom:4px"><b style="font-size:13px">&#9889; Energie &amp; Defense</b><span style="font-size:10px;color:#16a34a;font-weight:700;font-family:monospace">POSITIF</span></div>'+
        '<p style="margin:0;font-size:12px;color:#444;line-height:1.5">TotalEnergies beneficie du petrole. Thales et Dassault Aviation profitent du rearmement EU (+30% budgets). Safran remontee cadence Airbus.</p></div>'+
        '<div style="background:#fff;border-left:3px solid #16a34a;padding:11px 14px;margin-bottom:10px">'+
        '<div style="display:flex;justify-content:space-between;margin-bottom:4px"><b style="font-size:13px">&#128138; Sante &amp; Pharma</b><span style="font-size:10px;color:#16a34a;font-weight:700;font-family:monospace">POSITIF</span></div>'+
        '<p style="margin:0;font-size:12px;color:#444;line-height:1.5">Novo Nordisk reste le dossier Ozempic/Wegovy. Ipsen et Virbac en croissance reguliere. Pipeline biotech en acceleration.</p></div>'+
        '<div style="background:#fff;border-left:3px solid #d97706;padding:11px 14px;">'+
        '<div style="display:flex;justify-content:space-between;margin-bottom:4px"><b style="font-size:13px">&#128295; Industrie &amp; Transition</b><span style="font-size:10px;color:#d97706;font-weight:700;font-family:monospace">MIXTE</span></div>'+
        '<p style="margin:0;font-size:12px;color:#444;line-height:1.5">Schneider et Legrand sur la transition energetique. Equipementiers auto sous pression. ID Logistics et Stef resilients.</p></div>'
    )
    
    cal_rows="".join(
        '<tr><td style="padding:7px 12px;border-bottom:1px solid #eee;font-weight:600;font-size:12px;color:#1a3a5c;white-space:nowrap">'+d+"</td>"
        +'<td style="padding:7px 12px;border-bottom:1px solid #eee;font-size:12px">'+ev+"</td>"
        +'<td style="padding:7px 12px;border-bottom:1px solid #eee;font-size:11px;color:#666">'+det+"</td></tr>"
        for d,ev,det in [
            ("Lundi","PMI Manufacturier EU et US","Fort - indicateur avance activite industrie"),
            ("Mardi","Confiance consommateurs US","Moyen - barometre conso americaine"),
            ("Mercredi","CPI Inflation Zone Euro","Fort - donnees BCE, impact taux"),
            ("Jeudi","Claims chomage US","Moyen - sante marche emploi"),
            ("Vendredi","NFP Emploi US","TRES FORT - mouvement violent possible"),
        ]
    )
    
    grade_a_html = build_grade_a_section()
    
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:12px;background:#f5f3ef;font-family:Georgia,serif;color:#1a1a1a">
<div style="max-width:700px;margin:0 auto;background:#fff;box-shadow:0 2px 20px rgba(0,0,0,.08)">

<div style="background:linear-gradient(135deg,#0f2540,#1a3a5c);padding:26px 32px">
  <div style="font-family:Georgia,serif;font-size:22px;font-weight:700;color:#f0d080;letter-spacing:3px">PEA SCREENER PRO</div>
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:3px;margin-top:4px">JOURNAL FINANCIER HEBDOMADAIRE &middot; """ + w_label + """</div>
  <div style="margin-top:8px;font-size:12px;color:rgba(255,255,255,.6)">Marches &middot; Vos actions &middot; Analyses Grade A &middot; Actualites &middot; Agenda</div>
</div>

<!-- EDITORIAL DE LA SEMAINE -->
<div style="padding:18px 32px;background:#fdf8ec;border-bottom:2px solid #b8860b">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:10px">&#128241; Editorial de la semaine</div>
  <div style="font-size:13px;line-height:1.8;color:#1a1a1a;font-style:italic">""" + market_resume + """ Les actions en zone achat cette semaine meritent une attention particuliere - c est dans ces moments que se construisent les portefeuilles de long terme.</div>
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9312; Marches Mondiaux &mdash; Bilan semaine</div>
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="background:#f5f3ef">
      <th style="padding:7px 14px;text-align:left;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Marche</th>
      <th style="padding:7px 14px;text-align:right;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Vendredi</th>
      <th style="padding:7px 14px;text-align:right;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Semaine</th>
    </tr></thead>
    <tbody>""" + mrows + """</tbody>
  </table>
</div>

<div style="padding:0 32px 22px;background:#fafaf8">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9313; Votre Portefeuille PEA &mdash; Tops &amp; Flops</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div><div style="font-family:monospace;font-size:9px;color:#16a34a;margin-bottom:8px;text-transform:uppercase">&#128200; Top 5 hausses</div><table style="width:100%;border-collapse:collapse">""" + top_rows + """</table></div>
    <div><div style="font-family:monospace;font-size:9px;color:#ef4444;margin-bottom:8px;text-transform:uppercase">&#128201; Top 5 baisses</div><table style="width:100%;border-collapse:collapse">""" + bot_rows + """</table></div>
  </div>
  <div style="margin-top:14px;text-align:center"><a href="https://valval73.github.io/vacances/" target="_blank" style="display:inline-block;padding:9px 22px;background:#0f2540;color:#f0d080;font-family:monospace;font-size:10px;text-decoration:none;border-radius:3px;font-weight:700;letter-spacing:1px">&#128202; SCREENER COMPLET &#8594;</a></div>
</div>

<!-- ANALYSES GRADE A -->
<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:16px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#127942; Analyse Approfondie &mdash; Pepites Grade A</div>
  <div style="font-size:12px;color:#555;margin-bottom:14px;font-style:italic">Ces 4 titres representent la conviction la plus forte du Cabinet PEA Screener. Comprendre POURQUOI investir, pas seulement les chiffres.</div>
  """ + grade_a_html + """
</div>

<div style="padding:0 32px 22px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:16px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9314; Actualites Financieres</div>
  <div style="margin-bottom:16px">
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">&#127467;&#127479; Yahoo Finance France</div>""" + art_block(art_yahoo) + """
  </div>
  <div style="margin-bottom:16px">
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">&#128202; Boursorama Bourse</div>""" + art_block(art_bourso) + """
  </div>
  <div>
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">&#128269; Zone Bourse</div>""" + art_block(art_zb) + """
  </div>
</div>

<div style="padding:0 32px 22px;background:#fafaf8">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9315; Themes Macro &amp; Sectoriels</div>
  """ + themes_html + """
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9316; Agenda Macro &mdash; Semaine prochaine</div>
  <table style="width:100%;border-collapse:collapse">""" + cal_rows + """</table>
</div>

<div style="padding:0 32px 22px">
  <div style="background:#f0ede0;border-left:3px solid #b8860b;padding:13px 15px;font-size:12px;color:#444;line-height:1.8">
    <b style="color:#1a3a5c">&#128161; Regles d Or PEA Screener Pro</b><br>
    &#127984; MM200 : N achetez pas un titre en tendance baissiere<br>
    &#128202; R/R &#8805; 2x : Pour 1&#8364; risque, exigez 2&#8364; de potentiel<br>
    &#127919; Piotroski &#8805; 7 + Zone achat = Signal FORT<br>
    &#9203; PEA = horizon 5 ans &mdash; La patience bat le trading 95% du temps
  </div>
</div>

<div style="background:#0f2540;padding:16px 32px;text-align:center">
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:2px">PEA SCREENER PRO &middot; CABINET QUANTITATIF</div>
  <div style="margin-top:4px;font-size:10px;color:rgba(255,255,255,.25)">Document educatif &mdash; Pas de conseil en investissement agree AMF</div>
  <a href="https://valval73.github.io/vacances/" style="display:inline-block;margin-top:6px;color:#f0d080;font-size:11px;text-decoration:none">valval73.github.io/vacances</a>
</div>

</div></body></html>"""

def get_news():
    ay,ab,az=[],[],[]
    try:
        req=urllib.request.Request("https://fr.finance.yahoo.com/actualites/",headers={"User-Agent":"Mozilla/5.0","Accept-Language":"fr-FR,fr;q=0.9"})
        html=urllib.request.urlopen(req,timeout=14).read().decode("utf-8","ignore")
        for link,title in re.findall(r'href="(/actualites/[^"]+)"[^>]*>([^<]{30,180})<',html):
            t=re.sub(r"\s+"," ",title).strip()
            if len(t)>25 and t not in [x for _,x in ay]:
                ay.append(("https://fr.finance.yahoo.com"+link,t))
            if len(ay)>=5: break
    except Exception as e: print("Yahoo:"+str(e))
    try:
        req=urllib.request.Request("https://www.boursorama.com/bourse/actualites/",headers={"User-Agent":"Mozilla/5.0"})
        html=urllib.request.urlopen(req,timeout=14).read().decode("utf-8","ignore")
        for link,title in re.findall(r'href="(/bourse/actualites/[^"]+)"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})',html):
            t=re.sub(r"\s+"," ",title).strip()
            if len(t)>25 and t not in [x for _,x in ab]:
                ab.append(("https://www.boursorama.com"+link,t))
            if len(ab)>=5: break
    except Exception as e: print("Bourso:"+str(e))
    try:
        req=urllib.request.Request("https://www.zonebourse.com/actualite-bourse/",headers={"User-Agent":"Mozilla/5.0"})
        html=urllib.request.urlopen(req,timeout=14).read().decode("utf-8","ignore")
        for link,title in re.findall(r'href="(/actualite-bourse/[^"]+)"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})',html):
            t=re.sub(r"\s+"," ",title).strip()
            if len(t)>25 and t not in [x for _,x in az]:
                az.append(("https://www.zonebourse.com"+link,t))
            if len(az)>=5: break
    except Exception as e: print("ZB:"+str(e))
    return ay,ab,az

if __name__=="__main__":
    print("Journal Financier "+datetime.now().strftime("%d/%m/%Y %H:%M"))
    markets={}
    for name,ticker in INDICES.items():
        d=fetch_yahoo(ticker)
        if d: markets[name]=d
        time.sleep(0.2)
    print(str(len(markets))+" marches")
    pea={}
    for ticker,(name,yf) in PEA_WATCHLIST.items():
        d=fetch_yahoo(yf)
        if d: pea[ticker]={"name":name,**d}
        time.sleep(0.2)
    print(str(len(pea))+" actions PEA")
    ay,ab,az=get_news()
    print(str(len(ay))+" Yahoo / "+str(len(ab))+" Bourso / "+str(len(az))+" ZB")
    html=build_html(markets,pea,ay,ab,az)
    if not PASSWORD:
        with open("newsletter_preview.html","w",encoding="utf-8") as f: f.write(html)
        print("Preview: newsletter_preview.html")
    else:
        msg=MIMEMultipart("alternative")
        msg["Subject"]="PEA Pro - Journal "+datetime.now().strftime("%d/%m/%Y")+" - Analyses Grade A"
        msg["From"]=SENDER
        msg["To"]=RECIPIENT
        msg.attach(MIMEText(html,"html","utf-8"))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
                s.login(SENDER,PASSWORD)
                s.sendmail(SENDER,RECIPIENT,msg.as_string())
            print("Envoye a "+RECIPIENT)
        except Exception as e:
            print("Erreur: "+str(e))
            raise
