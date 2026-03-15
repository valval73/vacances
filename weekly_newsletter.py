#!/usr/bin/env python3
"""PEA Screener Pro — Newsletter Hebdomadaire Enrichie
Envoi samedi 8h vers romence1@gmail.com
- Marchés mondiaux avec variations semaine
- Vos 20 actions PEA (Top5 / Flop5)
- Articles Yahoo Finance / Boursorama / Zone Bourse
- Thèmes macro sectoriels
- Agenda semaine prochaine
"""
import json, urllib.request, smtplib, os, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

RECIPIENT = "romence1@gmail.com"
SENDER    = "romence1@gmail.com"
PASSWORD  = os.environ.get("GMAIL_PASSWORD", "")

INDICES = {
    "CAC 40": "^FCHI",
    "Euro Stoxx 50": "^STOXX50E",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "S&P 500": "^GSPC",
    "Nasdaq 100": "^NDX",
    "Or $/oz": "GC=F",
    "Petrole Brent": "BZ=F",
    "EUR/USD": "EURUSD=X",
    "Taux US 10 ans": "^TNX",
    "Bitcoin": "BTC-USD",
    "VIX (Peur)": "^VIX",
}

PEA_WATCHLIST = {
    "MC":   ("LVMH",             "MC.PA"),
    "AI":   ("Air Liquide",      "AI.PA"),
    "OR":   ("LOreal",           "OR.PA"),
    "RMS":  ("Hermes",           "RMS.PA"),
    "SAF":  ("Safran",           "SAF.PA"),
    "GTT":  ("GTT",              "GTT.PA"),
    "COFA": ("Coface",           "COFA.PA"),
    "TTE":  ("TotalEnergies",    "TTE.PA"),
    "LR":   ("Legrand",          "LR.PA"),
    "DG":   ("Vinci",            "DG.PA"),
    "SU":   ("Schneider",        "SU.PA"),
    "BNP":  ("BNP Paribas",      "BNP.PA"),
    "DASSAV": ("Dassault Avia",  "AM.PA"),
    "DSY":  ("Dassault Sys",     "DSY.PA"),
    "ASML": ("ASML",             "ASML.AS"),
    "NOVO": ("Novo Nordisk",     "NOVO-B.CO"),
    "ALV":  ("Allianz",          "ALV.DE"),
    "VIRBAC": ("Virbac",         "VIRP.PA"),
    "STEF": ("STEF",             "STF.PA"),
    "INTERPARFUMS": ("Interparfums", "ITP.PA"),
}


def fetch_yahoo(ticker):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/" + ticker + "?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta = data["chart"]["result"][0]["meta"]
        price = round(meta.get("regularMarketPrice", 0), 2)
        prev = meta.get("previousClose", price)
        week = meta.get("chartPreviousClose", price)
        chg_day  = round((price - prev) / prev * 100, 2) if prev else 0
        chg_week = round((price - week) / week * 100, 2) if week else 0
        return {"price": price, "chg_day": chg_day, "chg_week": chg_week}
    except Exception as e:
        print("  Yahoo error " + ticker + ": " + str(e))
        return None


def fetch_news(url, base=""):
    articles = []
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "fr-FR,fr;q=0.9"
        })
        with urllib.request.urlopen(req, timeout=14) as r:
            html = r.read().decode("utf-8", errors="ignore")
        # Extract links + titles via regex
        pattern = r'href="([^"]{10,200})"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})' 
        for link, title in re.findall(pattern, html):
            title = re.sub(r"\s+", " ", title).strip()
            if len(title) >= 30 and "cookie" not in title.lower() and "javascript" not in title.lower():
                full_url = (base + link) if link.startswith("/") else link
                if full_url not in [u for u, _ in articles]:
                    articles.append((full_url, title))
            if len(articles) >= 6:
                break
    except Exception as e:
        print("  News error " + url[:50] + ": " + str(e))
    return articles[:5]


def arrow(chg):
    if chg is None:
        return '<span style="color:#888">--</span>'
    col = "#22c55e" if chg > 0 else "#ef4444" if chg < -0.05 else "#888"
    sign = "+" if chg > 0 else ""
    arr = "&#9650;" if chg > 0.2 else "&#9660;" if chg < -0.2 else "&#9670;"
    return '<span style="color:' + col + ';font-weight:700">' + arr + " " + sign + str(chg) + '%</span>'


def build_html(markets, pea, art_yahoo, art_bourso, art_zb):
    now = datetime.now()
    week_label = (now - timedelta(days=6)).strftime("%d/%m") + " au " + now.strftime("%d/%m/%Y")

    # --- Marchés ---
    mrows = ""
    for name, d in markets.items():
        if not d:
            continue
        p = d["price"]
        pf = "{:,.0f}".format(p) if p > 1000 else "{:.4f}".format(p) if p < 2 else "{:.2f}".format(p)
        mrows += (
            '<tr><td style="padding:7px 14px;border-bottom:1px solid #eee;font-size:13px">' + name + "</td>"
            + '<td style="padding:7px 14px;border-bottom:1px solid #eee;text-align:right;font-family:monospace;font-size:13px">' + pf + "</td>"
            + '<td style="padding:7px 14px;border-bottom:1px solid #eee;text-align:right;font-size:13px">' + arrow(d.get("chg_week")) + "</td></tr>"
        )

    # --- PEA top/flop ---
    sorted_pea = sorted(pea.items(), key=lambda x: x[1].get("chg_week", 0), reverse=True)

    def prow(t, d):
        return (
            '<tr><td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;font-size:12px">'
            + '<b style="font-family:monospace;color:#0f2540">' + t + "</b> "
            + '<span style="color:#888;font-size:11px">' + d.get("name", "") + "</span></td>"
            + '<td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;font-family:monospace;font-size:12px;text-align:right">' + "{:.2f}".format(d["price"]) + "&#8364;</td>"
            + '<td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;text-align:right;font-size:12px">' + arrow(d.get("chg_week")) + "</td></tr>"
        )

    top_rows = "".join(prow(t, d) for t, d in sorted_pea[:5])
    bot_rows = "".join(prow(t, d) for t, d in sorted_pea[-5:])

    # --- Articles ---
    def art_block(arts):
        if not arts:
            return '<p style="color:#888;font-size:12px;font-style:italic">Indisponible cette semaine</p>'
        return "".join(
            '<div style="padding:7px 0;border-bottom:1px solid #f0f0f0"><a href="' + u + '" target="_blank" style="color:#1a3a5c;text-decoration:none;font-size:12px;line-height:1.5">&#8594; ' + t + "</a></div>"
            for u, t in arts
        )

    # --- Themes ---
    themes = [
        ("Banques & Taux BCE", "La trajectoire des taux BCE determine directement la marge nette des banques. BNP, Credit Agricole et SocGen sont directement exposes.", "BNP, ACA, GLE", "#1d4ed8", "Surveiller"),
        ("Energie & Defense", "TotalEnergies beneficie du petrole. Thales et Dassault Aviation profitent du rearmement EU (+30% budgets depuis 2022).", "TTE, HO, DASSAV", "#16a34a", "Positif"),
        ("Sante & Pharma", "Novo Nordisk reste le dossier Ozempic/Wegovy. Sanofi accelere en oncologie. Virbac profite de l humanisation des animaux.", "SAN, NOVO, VIRBAC", "#16a34a", "Positif"),
        ("Industrie & Transition", "Schneider Electric et Legrand beneficient de la transition energetique. Equipementiers auto sous pression.", "SU, LR, VALO", "#d97706", "Mixte"),
    ]
    theme_html = ""
    verdict_colors = {"Positif": "#16a34a", "Surveiller": "#d97706", "Mixte": "#6b7280", "Negatif": "#dc2626"}
    for sector, desc, acts, col, verdict in themes:
        vc = verdict_colors.get(verdict, "#888")
        theme_html += (
            '<div style="background:#fff;border-left:3px solid ' + col + ';padding:11px 14px;margin-bottom:10px">'
            + '<div style="display:flex;justify-content:space-between;margin-bottom:4px"><b style="font-size:13px">&#128288; ' + sector + "</b>"
            + '<span style="font-size:10px;color:' + vc + ';font-weight:700;font-family:monospace">' + verdict.upper() + "</span></div>"
            + '<p style="margin:0 0 5px;font-size:12px;color:#444;line-height:1.5">' + desc + "</p>"
            + '<div style="font-size:11px;color:#888">Actions : ' + acts + "</div></div>"
        )

    # --- Agenda ---
    cal = [
        ("Lundi",   "PMI Manufacturier EU et US",     "Fort - indicateur avance activite industrie"),
        ("Mardi",   "Confiance consommateurs US",      "Moyen - barometre conso americaine"),
        ("Mercredi","CPI Inflation Zone Euro",         "Fort - donnees BCE, impact direct sur taux"),
        ("Jeudi",   "Claims chomage US",               "Moyen - sante marche emploi"),
        ("Vendredi","NFP Emploi US",                   "TRES FORT - mouvement violent possible"),
    ]
    cal_rows = "".join(
        '<tr><td style="padding:7px 12px;border-bottom:1px solid #eee;font-weight:600;font-size:12px;color:#1a3a5c;white-space:nowrap">' + d + "</td>"
        + '<td style="padding:7px 12px;border-bottom:1px solid #eee;font-size:12px">' + ev + "</td>"
        + '<td style="padding:7px 12px;border-bottom:1px solid #eee;font-size:11px;color:#666">' + det + "</td></tr>"
        for d, ev, det in cal
    )

    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:12px;background:#f5f3ef;font-family:Georgia,serif;color:#1a1a1a">
<div style="max-width:700px;margin:0 auto;background:#fff;box-shadow:0 2px 20px rgba(0,0,0,.08)">

<div style="background:linear-gradient(135deg,#0f2540,#1a3a5c);padding:26px 32px">
  <div style="font-family:Georgia,serif;font-size:22px;font-weight:700;color:#f0d080;letter-spacing:3px">PEA SCREENER PRO</div>
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:3px;margin-top:4px">NEWSLETTER HEBDOMADAIRE &middot; """ + week_label + """</div>
  <div style="margin-top:8px;font-size:12px;color:rgba(255,255,255,.6)">Marches &middot; Vos actions &middot; Actualites &middot; Macro &middot; Agenda</div>
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9312; Marches Mondiaux &mdash; Performance semaine</div>
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="background:#f5f3ef">
      <th style="padding:7px 14px;text-align:left;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Marche</th>
      <th style="padding:7px 14px;text-align:right;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Cours</th>
      <th style="padding:7px 14px;text-align:right;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Semaine</th>
    </tr></thead>
    <tbody>""" + mrows + """</tbody>
  </table>
</div>

<div style="padding:0 32px 22px;background:#fafaf8">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9313; Vos Actions PEA &mdash; Tops &amp; Flops semaine</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div>
      <div style="font-family:monospace;font-size:9px;color:#16a34a;margin-bottom:8px;text-transform:uppercase">&#128200; Top 5 hausses</div>
      <table style="width:100%;border-collapse:collapse">""" + top_rows + """</table>
    </div>
    <div>
      <div style="font-family:monospace;font-size:9px;color:#ef4444;margin-bottom:8px;text-transform:uppercase">&#128201; Top 5 baisses</div>
      <table style="width:100%;border-collapse:collapse">""" + bot_rows + """</table>
    </div>
  </div>
  <div style="margin-top:14px;text-align:center">
    <a href="https://valval73.github.io/vacances/" target="_blank" style="display:inline-block;padding:9px 22px;background:#0f2540;color:#f0d080;font-family:monospace;font-size:10px;text-decoration:none;border-radius:3px;font-weight:700;letter-spacing:1px">&#128202; SCREENER COMPLET &#8594;</a>
  </div>
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:16px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9314; Actualites Financieres</div>
  <div style="margin-bottom:16px">
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">&#127467;&#127479; Yahoo Finance France</div>
    """ + art_block(art_yahoo) + """
  </div>
  <div style="margin-bottom:16px">
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">&#128202; Boursorama Bourse</div>
    """ + art_block(art_bourso) + """
  </div>
  <div>
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">&#128269; Zone Bourse</div>
    """ + art_block(art_zb) + """
  </div>
</div>

<div style="padding:0 32px 22px;background:#fafaf8">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9315; Themes Macro &amp; Sectoriels</div>
  """ + theme_html + """
</div>


  <div style="padding:0 32px 22px">
    <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#128218; Analyse Approfondie &mdash; Pepites Grade A</div>
    <div style="background:#fff;border:1px solid #e8e0d5;border-radius:5px;margin-bottom:10px;overflow:hidden">
      <div style="background:#0f2540;padding:9px 14px;display:flex;justify-content:space-between;align-items:center"><b style="color:#f0d080;font-family:monospace;font-size:12px">AI &mdash; Air Liquide</b><span style="background:#22c55e;color:#fff;font-family:monospace;font-size:8px;padding:2px 7px;border-radius:3px">GRADE A</span></div>
      <div style="padding:11px 14px;font-size:12px;line-height:1.7;color:#1a1a1a"><b>Moat :</b> Duopole mondial gaz industriels avec Linde. Pipelines impossibles a dupliquer, contrats 15-20 ans indexes inflation, switching cost absolu pour les clients chimie/sante/semi.<br><b>Catalyseurs 2026 :</b> H2 vert (35 projets), semi-conducteurs ultra-purs, sante vieillissement EU. ROE 18%, Piotroski 8/9, dividende en hausse depuis 40 ans.<br><b>Zone achat : 145-162 euros. Stop 132 euros. Objectif 178 euros.</b></div>
      <div style="padding:0 14px 10px;display:flex;gap:6px"><a href="https://fr.tradingview.com/chart/?symbol=EURONEXT:AI&interval=W" target="_blank" style="padding:4px 9px;background:#b8860b;color:#fff;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">TradingView</a><a href="https://www.zonebourse.com/recherche/?q=Air+Liquide" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Zone Bourse</a><a href="https://www.morningstar.fr/fr/stocks/xpar/ai/quote.aspx" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Morningstar</a></div>
    </div>
    <div style="background:#fff;border:1px solid #e8e0d5;border-radius:5px;margin-bottom:10px;overflow:hidden">
      <div style="background:#0f2540;padding:9px 14px;display:flex;justify-content:space-between;align-items:center"><b style="color:#f0d080;font-family:monospace;font-size:12px">GTT &mdash; Gaztransport Technigaz</b><span style="background:#22c55e;color:#fff;font-family:monospace;font-size:8px;padding:2px 7px;border-radius:3px">GRADE A</span></div>
      <div style="padding:11px 14px;font-size:12px;line-height:1.7;color:#1a1a1a"><b>Moat :</b> Brevets des membranes cryogeniques sur 90% des methaniers mondiaux. ROE 85%, marge nette 58%, zero CAPEX (pure IP). 850 navires commandes 2026-2030.<br><b>Catalyseurs 2026 :</b> Carnet record 45 navires/an, expansion reservoirs H2/NH3, renouvellement contrats. Hermes de l energie.<br><b>Zone achat : 188-218 euros. Stop 168 euros. Objectif 265 euros.</b></div>
      <div style="padding:0 14px 10px;display:flex;gap:6px"><a href="https://fr.tradingview.com/chart/?symbol=EURONEXT:GTT&interval=W" target="_blank" style="padding:4px 9px;background:#b8860b;color:#fff;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">TradingView</a><a href="https://www.zonebourse.com/recherche/?q=GTT+Gaztransport" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Zone Bourse</a><a href="https://www.morningstar.fr/fr/stocks/xpar/gtt/quote.aspx" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Morningstar</a></div>
    </div>
    <div style="background:#fff;border:1px solid #e8e0d5;border-radius:5px;margin-bottom:10px;overflow:hidden">
      <div style="background:#0f2540;padding:9px 14px;display:flex;justify-content:space-between;align-items:center"><b style="color:#f0d080;font-family:monospace;font-size:12px">SAF &mdash; Safran</b><span style="background:#22c55e;color:#fff;font-family:monospace;font-size:8px;padding:2px 7px;border-radius:3px">GRADE A</span></div>
      <div style="padding:11px 14px;font-size:12px;line-height:1.7;color:#1a1a1a"><b>Moat :</b> Co-fab moteur LEAP (70% A320/737 neufs). Chaque moteur = 30 ans de MRO a l heure de vol. La flotte mondiale double d ici 2040. Rente perpetuelle aviation civile.<br><b>Catalyseurs 2026 :</b> MRO LEAP maturite (+25% recurrents), cadence Airbus 75/mois, programme RISE moteur ouvert. Piotroski 8/9.<br><b>Zone achat : 225-255 euros. Stop 200 euros. Objectif 310 euros.</b></div>
      <div style="padding:0 14px 10px;display:flex;gap:6px"><a href="https://fr.tradingview.com/chart/?symbol=EURONEXT:SAF&interval=W" target="_blank" style="padding:4px 9px;background:#b8860b;color:#fff;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">TradingView</a><a href="https://www.zonebourse.com/recherche/?q=Safran" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Zone Bourse</a><a href="https://www.morningstar.fr/fr/stocks/xpar/saf/quote.aspx" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Morningstar</a></div>
    </div>
    <div style="background:#fff;border:1px solid #e8e0d5;border-radius:5px;overflow:hidden">
      <div style="background:#0f2540;padding:9px 14px;display:flex;justify-content:space-between;align-items:center"><b style="color:#f0d080;font-family:monospace;font-size:12px">ASML &mdash; Lithographie EUV</b><span style="background:#22c55e;color:#fff;font-family:monospace;font-size:8px;padding:2px 7px;border-radius:3px">GRADE A</span></div>
      <div style="padding:11px 14px;font-size:12px;line-height:1.7;color:#1a1a1a"><b>Moat :</b> Monopole absolu de la lithographie EUV. TSMC/Samsung/Intel ne peuvent pas produire de puces sub-7nm sans ASML. Aucun concurrent a horizon 15 ans. 440 milliards de CA carnet.<br><b>Catalyseurs 2026 :</b> Reprise commandes TSMC (IA chips), EUV High-NA deploiement, expansion Etats-Unis. Correction -30% depuis le pic = opportunite.<br><b>Zone achat : 580-660 euros. Stop 540 euros. Objectif 780 euros. Eligible PEA via AEX Amsterdam.</b></div>
      <div style="padding:0 14px 10px;display:flex;gap:6px"><a href="https://fr.tradingview.com/chart/?symbol=NASDAQ:ASML&interval=W" target="_blank" style="padding:4px 9px;background:#b8860b;color:#fff;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">TradingView</a><a href="https://www.zonebourse.com/recherche/?q=ASML" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Zone Bourse</a><a href="https://www.morningstar.fr/fr/stocks/xams/asml/quote.aspx" target="_blank" style="padding:4px 9px;background:#f0f0f0;color:#1a3a5c;font-family:monospace;font-size:9px;text-decoration:none;border-radius:3px">Morningstar</a></div>
    </div>
    <div style="margin-top:10px;text-align:center;font-size:11px;color:#888;font-style:italic">125 actions analysees &mdash; <a href="https://valval73.github.io/vacances/" style="color:#b8860b">Voir le screener complet</a></div>
  </div>
<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">&#9316; Agenda Macro &mdash; Semaine prochaine</div>
  <table style="width:100%;border-collapse:collapse">""" + cal_rows + """</table>
</div>

<div style="padding:0 32px 22px">
  <div style="background:#f0ede0;border-left:3px solid #b8860b;padding:13px 15px;font-size:12px;color:#444;line-height:1.8">
    <b style="color:#1a3a5c">&#128161; Regles d Or PEA Screener Pro</b><br>
    &#127984; <b>MM200</b> : N achetez pas un titre en tendance baissiere (cours sous MM200)<br>
    &#128202; <b>R/R &ge; 2x</b> : Pour 1&#8364; risque, exigez 2&#8364; de potentiel minimum<br>
    &#127919; <b>Piotroski &ge; 7 + Zone achat</b> = Signal FORT<br>
    &#9203; <b>PEA = horizon 5 ans</b> &mdash; La patience bat le trading actif 95% du temps
  </div>
</div>

<div style="background:#0f2540;padding:16px 32px;text-align:center">
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:2px">PEA SCREENER PRO &middot; CABINET QUANTITATIF</div>
  <div style="margin-top:4px;font-size:10px;color:rgba(255,255,255,.25)">Document educatif &mdash; Pas de conseil en investissement agree AMF</div>
  <a href="https://valval73.github.io/vacances/" style="display:inline-block;margin-top:6px;color:#f0d080;font-size:11px;text-decoration:none">valval73.github.io/vacances</a>
</div>

</div></body></html>"""


def get_news():
    art_y, art_b, art_z = [], [], []
    # Yahoo Finance France
    try:
        req = urllib.request.Request(
            "https://fr.finance.yahoo.com/actualites/",
            headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "fr-FR,fr;q=0.9"}
        )
        html = urllib.request.urlopen(req, timeout=14).read().decode("utf-8", errors="ignore")
        for link, title in re.findall(r'href="(/actualites/[^"]+)"[^>]*>([^<]{30,180})<', html):
            t = re.sub(r"\s+", " ", title).strip()
            if len(t) > 25 and t not in [x for _, x in art_y]:
                art_y.append(("https://fr.finance.yahoo.com" + link, t))
            if len(art_y) >= 5:
                break
    except Exception as e:
        print("Yahoo news: " + str(e))
    # Boursorama
    try:
        req = urllib.request.Request(
            "https://www.boursorama.com/bourse/actualites/",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req, timeout=14).read().decode("utf-8", errors="ignore")
        for link, title in re.findall(r'href="(/bourse/actualites/[^"]+)"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})', html):
            t = re.sub(r"\s+", " ", title).strip()
            if len(t) > 25 and t not in [x for _, x in art_b]:
                art_b.append(("https://www.boursorama.com" + link, t))
            if len(art_b) >= 5:
                break
    except Exception as e:
        print("Boursorama news: " + str(e))
    # Zone Bourse
    try:
        req = urllib.request.Request(
            "https://www.zonebourse.com/actualite-bourse/",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        html = urllib.request.urlopen(req, timeout=14).read().decode("utf-8", errors="ignore")
        for link, title in re.findall(r'href="(/actualite-bourse/[^"]+)"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})', html):
            t = re.sub(r"\s+", " ", title).strip()
            if len(t) > 25 and t not in [x for _, x in art_z]:
                art_z.append(("https://www.zonebourse.com" + link, t))
            if len(art_z) >= 5:
                break
    except Exception as e:
        print("ZoneBourse news: " + str(e))
    return art_y, art_b, art_z


if __name__ == "__main__":
    print("Newsletter " + datetime.now().strftime("%d/%m/%Y %H:%M"))
    markets = {}
    for name, ticker in INDICES.items():
        d = fetch_yahoo(ticker)
        if d:
            markets[name] = d
        time.sleep(0.2)
    print(str(len(markets)) + " marches")
    pea = {}
    for ticker, (name, yf) in PEA_WATCHLIST.items():
        d = fetch_yahoo(yf)
        if d:
            pea[ticker] = {"name": name, **d}
        time.sleep(0.2)
    print(str(len(pea)) + " actions PEA")
    art_y, art_b, art_z = get_news()
    print(str(len(art_y)) + " Yahoo / " + str(len(art_b)) + " Bourso / " + str(len(art_z)) + " ZB")
    html = build_html(markets, pea, art_y, art_b, art_z)
    if not PASSWORD:
        with open("newsletter_preview.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Preview sauvegarde: newsletter_preview.html")
    else:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "PEA Pro - Hebdo " + datetime.now().strftime("%d/%m/%Y")
        msg["From"] = SENDER
        msg["To"] = RECIPIENT
        msg.attach(MIMEText(html, "html", "utf-8"))
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER, PASSWORD)
                server.sendmail(SENDER, RECIPIENT, msg.as_string())
            print("Envoye a " + RECIPIENT)
        except Exception as e:
            print("Erreur envoi: " + str(e))
            raise
