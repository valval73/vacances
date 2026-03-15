#!/usr/bin/env python3
"""
PEA Screener Pro — Newsletter hebdomadaire automatique
Envoi chaque samedi à 8h via GitHub Actions
Récupère données macro + marchés + génère analyse IA
Envoie à romence1@gmail.com
"""
import json, urllib.request, urllib.parse, smtplib, os, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

RECIPIENT = "romence1@gmail.com"
SENDER    = "romence1@gmail.com"
PASSWORD  = os.environ.get("GMAIL_PASSWORD", "")  # GitHub Secret

# ══════════════════════════════════════════
# 1. RÉCUPÉRATION DES DONNÉES MARCHÉ
# ══════════════════════════════════════════

def fetch_yahoo(ticker, name):
    """Récupère cours + variation hebdo depuis Yahoo Finance"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1wk&range=1mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        result = d["chart"]["result"][0]
        meta = result["meta"]
        price = round(meta.get("regularMarketPrice", 0), 2)
        prev_week = meta.get("chartPreviousClose", price)
        chg_week = round((price - prev_week) / prev_week * 100, 2) if prev_week else 0
        return {"name": name, "price": price, "chg": chg_week}
    except Exception as e:
        return {"name": name, "price": 0, "chg": 0, "error": str(e)}

def get_market_data():
    """Récupère les principaux indices et actifs"""
    markets = {
        "CAC 40": "^FCHI",
        "Euro Stoxx 50": "^STOXX50E",
        "S&P 500": "^GSPC",
        "Nasdaq 100": "^NDX",
        "DAX": "^GDAXI",
        "FTSE 100": "^FTSE",
        "Nikkei 225": "^N225",
        "Or ($/oz)": "GC=F",
        "Pétrole Brent": "BZ=F",
        "EUR/USD": "EURUSD=X",
        "Taux US 10 ans": "^TNX",
        "Bitcoin": "BTC-USD",
    }
    results = {}
    for name, ticker in markets.items():
        results[name] = fetch_yahoo(ticker, name)
        import time; time.sleep(0.3)
    return results

def get_pea_top_performers():
    """Top 5 meilleures et pires actions PEA de la semaine"""
    pea_tickers = {
        "MC": "LVMH", "AI": "Air Liquide", "OR": "L'Oréal", "SAF": "Safran",
        "SU": "Schneider", "GTT": "GTT", "COFA": "Coface", "TTE": "TotalEnergies",
        "DASSAV": "Dassault Aviation", "NEXANS": "Nexans", "BNP": "BNP Paribas",
        "AXA": "Axa", "DG": "Vinci", "LR": "Legrand", "SAN": "Sanofi"
    }
    yahoo_map = {
        "MC": "MC.PA", "AI": "AI.PA", "OR": "OR.PA", "SAF": "SAF.PA",
        "SU": "SU.PA", "GTT": "GTT.PA", "COFA": "COFA.PA", "TTE": "TTE.PA",
        "DASSAV": "AM.PA", "NEXANS": "NEX.PA", "BNP": "BNP.PA",
        "AXA": "CS.PA", "DG": "DG.PA", "LR": "LR.PA", "SAN": "SAN.PA"
    }
    perf = []
    for ticker, name in pea_tickers.items():
        d = fetch_yahoo(yahoo_map.get(ticker, ticker+".PA"), name)
        if d.get("price", 0) > 0:
            perf.append({"ticker": ticker, "name": name, "chg": d["chg"], "price": d["price"]})
        import time; time.sleep(0.3)
    perf.sort(key=lambda x: x["chg"], reverse=True)
    return perf[:5], perf[-5:]

# ══════════════════════════════════════════
# 2. GÉNÉRATION HTML DE LA NEWSLETTER
# ══════════════════════════════════════════

def color_chg(chg):
    if chg > 0: return "#1a6b3a"
    if chg < 0: return "#c0392b"
    return "#888888"

def arrow(chg):
    if chg > 1: return "▲"
    if chg < -1: return "▼"
    return "◆"

def build_html(markets, top5, bottom5):
    now = datetime.now()
    week_start = (now - timedelta(days=6)).strftime("%d/%m")
    week_end = now.strftime("%d/%m/%Y")
    
    # Market rows
    market_rows = ""
    for name, d in markets.items():
        chg = d.get("chg", 0)
        price = d.get("price", 0)
        if price == 0: continue
        col = color_chg(chg)
        ar = arrow(chg)
        market_rows += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #e8e0d5;font-weight:500">{name}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e8e0d5;text-align:right;font-family:monospace">{price:,.2f}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #e8e0d5;text-align:right;color:{col};font-family:monospace;font-weight:600">{ar} {chg:+.2f}%</td>
        </tr>"""

    # Top performers
    top_rows = ""
    for s in top5:
        col = color_chg(s["chg"])
        top_rows += f"""
        <tr>
          <td style="padding:6px 10px;border-bottom:1px solid #e8e0d5">
            <b style="font-family:monospace;color:#1a3a5c">{s['ticker']}</b>
            <span style="color:#888;font-size:11px;margin-left:6px">{s['name']}</span>
          </td>
          <td style="padding:6px 10px;border-bottom:1px solid #e8e0d5;text-align:right;font-family:monospace">{s['price']:.2f}€</td>
          <td style="padding:6px 10px;border-bottom:1px solid #e8e0d5;text-align:right;color:{col};font-weight:600;font-family:monospace">{s['chg']:+.2f}%</td>
        </tr>"""

    bottom_rows = ""
    for s in bottom5:
        col = color_chg(s["chg"])
        bottom_rows += f"""
        <tr>
          <td style="padding:6px 10px;border-bottom:1px solid #e8e0d5">
            <b style="font-family:monospace;color:#1a3a5c">{s['ticker']}</b>
            <span style="color:#888;font-size:11px;margin-left:6px">{s['name']}</span>
          </td>
          <td style="padding:6px 10px;border-bottom:1px solid #e8e0d5;text-align:right;font-family:monospace">{s['price']:.2f}€</td>
          <td style="padding:6px 10px;border-bottom:1px solid #e8e0d5;text-align:right;color:{col};font-weight:600;font-family:monospace">{s['chg']:+.2f}%</td>
        </tr>"""

    # Agenda semaine prochaine (fixe - clé events à venir)
    next_week = (now + timedelta(days=7)).strftime("%d/%m")
    
    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f3ef;font-family:Georgia,serif;color:#1a1a1a">
  <div style="max-width:680px;margin:0 auto;background:#fff;box-shadow:0 2px 20px rgba(0,0,0,.08)">
    
    <!-- HEADER -->
    <div style="background:linear-gradient(135deg,#0f2540,#1a3a5c);padding:28px 32px;text-align:center">
      <div style="font-family:Georgia,serif;font-size:22px;font-weight:700;color:#f0d080;letter-spacing:2px">
        PEA SCREENER PRO
      </div>
      <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:3px;margin-top:4px">
        NEWSLETTER HEBDOMADAIRE · {week_start} — {week_end}
      </div>
      <div style="margin-top:12px;font-size:13px;color:rgba(255,255,255,.7)">
        Récapitulatif marchés · Opportunités PEA · Agenda semaine
      </div>
    </div>

    <!-- INDICES MONDIAUX -->
    <div style="padding:24px 32px">
      <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#888;margin-bottom:12px;border-bottom:2px solid #b8860b;padding-bottom:6px">
        📊 Marchés & Indices — Semaine écoulée
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead>
          <tr style="background:#f5f3ef">
            <th style="padding:8px 12px;text-align:left;font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#888">Marché</th>
            <th style="padding:8px 12px;text-align:right;font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#888">Cours</th>
            <th style="padding:8px 12px;text-align:right;font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:1px;color:#888">Semaine</th>
          </tr>
        </thead>
        <tbody>{market_rows}</tbody>
      </table>
    </div>

    <!-- TOP PEA -->
    <div style="padding:0 32px 24px">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
        <div>
          <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:2px;color:#1a6b3a;margin-bottom:10px;border-bottom:2px solid #1a6b3a;padding-bottom:5px">
            📈 Top 5 PEA — Meilleures semaines
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:12px">
            <tbody>{top_rows}</tbody>
          </table>
        </div>
        <div>
          <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:2px;color:#c0392b;margin-bottom:10px;border-bottom:2px solid #c0392b;padding-bottom:5px">
            📉 Bottom 5 PEA — Plus fortes baisses
          </div>
          <table style="width:100%;border-collapse:collapse;font-size:12px">
            <tbody>{bottom_rows}</tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- THÈMES MACRO -->
    <div style="padding:0 32px 24px;background:#fafaf8">
      <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#888;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">
        🌍 Thèmes macro à surveiller — Semaine du {next_week}
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;font-size:12px">
        <div style="background:#fff;border-left:3px solid #1a3a5c;padding:10px 12px;border-radius:0 4px 4px 0">
          <div style="font-weight:700;color:#1a3a5c;margin-bottom:4px">🏦 Banques Centrales</div>
          <div style="color:#555;line-height:1.6">Surveiller les minutes Fed et discours BCE. Tout signal sur la trajectoire des taux impacte directement les valorisations.</div>
        </div>
        <div style="background:#fff;border-left:3px solid #b8860b;padding:10px 12px;border-radius:0 4px 4px 0">
          <div style="font-weight:700;color:#b8860b;margin-bottom:4px">📊 Données Macro</div>
          <div style="color:#555;line-height:1.6">PMI, emploi US, inflation EU. Les surprises macro sont les principaux moteurs de volatilité à court terme.</div>
        </div>
        <div style="background:#fff;border-left:3px solid #1a6b3a;padding:10px 12px;border-radius:0 4px 4px 0">
          <div style="font-weight:700;color:#1a6b3a;margin-bottom:4px">💰 Résultats d'Entreprises</div>
          <div style="color:#555;line-height:1.6">Season résultats : focus sur les guidances 2026. Les révisions de BPA sont le principal catalyseur d'une action.</div>
        </div>
        <div style="background:#fff;border-left:3px solid #c0392b;padding:10px 12px;border-radius:0 4px 4px 0">
          <div style="font-weight:700;color:#c0392b;margin-bottom:4px">⚠️ Risques Géopolitiques</div>
          <div style="color:#555;line-height:1.6">Tensions commerciales US/Chine, Ukraine, Moyen-Orient. Ces risques peuvent déclencher des spikes de volatilité.</div>
        </div>
      </div>
    </div>

    <!-- RÈGLES D'OR -->
    <div style="padding:16px 32px 24px">
      <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#888;margin-bottom:12px;border-bottom:2px solid #b8860b;padding-bottom:6px">
        💡 Règles d'Or de la Semaine — PEA Screener Pro
      </div>
      <div style="font-size:12px;color:#444;line-height:1.8;background:#f5efe0;padding:14px 16px;border-radius:4px;font-style:italic">
        🏰 <b>Ne jamais acheter au-dessus de la MM200</b> sur un titre en tendance baissière — attendre le retour en zone d'achat.<br>
        📊 <b>R/R minimum 2x</b> : pour chaque trade, le potentiel doit être 2x le risque (stop-loss).<br>
        🎯 <b>Score Piotroski ≥ 7 + Zone achat = signal FORT</b> — la convergence fondamentaux + technique réduit le risque.<br>
        ⏳ <b>PEA = horizon 5+ ans</b> : les meilleurs retours viennent de la patience, pas du trading actif.
      </div>
    </div>

    <!-- FOOTER -->
    <div style="background:#0f2540;padding:20px 32px;text-align:center">
      <div style="font-family:monospace;font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:2px">
        PEA Screener Pro · Cabinet Quantitatif · Données indicatives
      </div>
      <div style="margin-top:6px;font-size:10px;color:rgba(255,255,255,.3)">
        ⚠️ Document éducatif uniquement — Pas de conseil en investissement agréé AMF<br>
        <a href="https://valval73.github.io/vacances/" style="color:#f0d080;text-decoration:none">👉 Ouvrir le Screener PEA Pro →</a>
      </div>
    </div>

  </div>
</body>
</html>"""
    return html

# ══════════════════════════════════════════
# 3. ENVOI EMAIL
# ══════════════════════════════════════════

def send_email(html_content):
    if not PASSWORD:
        print("⚠️  GMAIL_PASSWORD non défini — email non envoyé")
        print("   Configure le secret dans GitHub Settings > Secrets")
        return False
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 PEA Screener Pro — Newsletter {datetime.now().strftime('%d/%m/%Y')}"
    msg["From"]    = SENDER
    msg["To"]      = RECIPIENT
    
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECIPIENT, msg.as_string())
        print(f"✅ Newsletter envoyée à {RECIPIENT}")
        return True
    except Exception as e:
        print(f"❌ Erreur envoi: {e}")
        return False

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

if __name__ == "__main__":
    print(f"📰 Génération newsletter {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    print("📊 Récupération données marchés...")
    markets = get_market_data()
    
    print("📈 Top/Bottom performers PEA...")
    top5, bottom5 = get_pea_top_performers()
    
    print("📧 Génération HTML...")
    html = build_html(markets, top5, bottom5)
    
    # Save HTML preview
    with open("newsletter_preview.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("💾 Aperçu sauvegardé: newsletter_preview.html")
    
    print("📤 Envoi email...")
    send_email(html)
