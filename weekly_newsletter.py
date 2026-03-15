#!/usr/bin/env python3
"""PEA Screener Pro — Newsletter Hebdomadaire ENRICHIE"""
import json, urllib.request, smtplib, os, re, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

RECIPIENT = "romence1@gmail.com"
SENDER    = "romence1@gmail.com"
PASSWORD  = os.environ.get("GMAIL_PASSWORD", "")

INDICES = {
    'CAC 40':'^FCHI','Euro Stoxx 50':'^STOXX50E','DAX':'^GDAXI',
    'FTSE 100':'^FTSE','S&P 500':'^GSPC','Nasdaq 100':'^NDX',
    'Or $/oz':'GC=F','Pétrole Brent':'BZ=F','EUR/USD':'EURUSD=X',
    'Taux US 10 ans':'^TNX','Bitcoin':'BTC-USD','VIX':'^VIX',
}

PEA_WATCHLIST = {
    'MC':('LVMH','MC.PA'),'AI':('Air Liquide','AI.PA'),'OR':(\"L'Oréal\",'OR.PA'),
    'RMS':('Hermès','RMS.PA'),'SAF':('Safran','SAF.PA'),'GTT':('GTT','GTT.PA'),
    'COFA':('Coface','COFA.PA'),'TTE':('TotalEnergies','TTE.PA'),
    'DSY':('Dassault Systèmes','DSY.PA'),'DASSAV':('Dassault Aviation','AM.PA'),
    'LR':('Legrand','LR.PA'),'DG':('Vinci','DG.PA'),'SU':('Schneider','SU.PA'),
    'BNP':('BNP Paribas','BNP.PA'),'VIRBAC':('Virbac','VIRP.PA'),
    'ASML':('ASML','ASML.AS'),'NOVO':('Novo Nordisk','NOVO-B.CO'),
    'ALV':('Allianz','ALV.DE'),'STEF':('STEF','STF.PA'),
    'INTERPARFUMS':('Interparfums','ITP.PA'),
}

def fetch_yahoo(ticker):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d'
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta = data['chart']['result'][0]['meta']
        price = round(meta.get('regularMarketPrice',0),2)
        prev = meta.get('previousClose',price)
        week = meta.get('chartPreviousClose',price)
        return {
            'price':price,
            'chg_day':round((price-prev)/prev*100,2) if prev else 0,
            'chg_week':round((price-week)/week*100,2) if week else 0,
        }
    except:
        return None

def fetch_news(url, pattern, base='', limit=5):
    articles = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Accept-Language':'fr-FR,fr;q=0.9'})
        with urllib.request.urlopen(req, timeout=12) as r:
            html = r.read().decode('utf-8', errors='ignore')
        for link, title in re.findall(pattern, html)[:12]:
            title = re.sub(r'\s+',' ',title).strip()
            if len(title) > 25 and title not in [t for _,t in articles]:
                articles.append((base+link, title))
            if len(articles) >= limit:
                break
    except Exception as e:
        print(f"  News error {url[:40]}: {e}")
    return articles

def arrow(chg):
    if chg is None: return '<span style="color:#888">—</span>'
    col = '#22c55e' if chg > 0 else '#ef4444' if chg < -0.05 else '#888'
    sign = '+' if chg > 0 else ''
    arr = '▲' if chg > 0.2 else '▼' if chg < -0.2 else '◆'
    return f'<span style="color:{col};font-weight:700">{arr} {sign}{chg:.2f}%</span>'

def build_html(markets, pea, art_yahoo, art_bourso, art_zb):
    now = datetime.now()
    w = f"{(now-timedelta(days=6)).strftime('%d/%m')} — {now.strftime('%d/%m/%Y')}"

    # Marchés rows
    mrows = ''
    for name, d in markets.items():
        if not d: continue
        p = d['price']
        pf = f"{p:,.0f}" if p > 1000 else f"{p:.4f}" if p < 2 else f"{p:.2f}"
        mrows += f'<tr><td style="padding:7px 14px;border-bottom:1px solid #eee;font-size:13px">{name}</td><td style="padding:7px 14px;border-bottom:1px solid #eee;text-align:right;font-family:monospace;font-size:13px">{pf}</td><td style="padding:7px 14px;border-bottom:1px solid #eee;text-align:right;font-size:13px">{arrow(d.get("chg_week"))}</td></tr>'

    # PEA top/flop
    sorted_pea = sorted(pea.items(), key=lambda x: x[1].get('chg_week',0), reverse=True)
    def prow(t, d):
        return f'<tr><td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;font-size:12px"><b style="font-family:monospace;color:#0f2540">{t}</b> <span style="color:#888;font-size:11px">{d["name"]}</span></td><td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;font-family:monospace;font-size:12px;text-align:right">{d["price"]:.2f}€</td><td style="padding:6px 8px;border-bottom:1px solid #f0f0f0;text-align:right;font-size:12px">{arrow(d.get("chg_week"))}</td></tr>'
    top_rows = ''.join(prow(t,d) for t,d in sorted_pea[:5])
    bot_rows = ''.join(prow(t,d) for t,d in sorted_pea[-5:])

    # Articles
    def art_block(arts):
        if not arts: return '<p style="color:#888;font-size:12px;font-style:italic">Indisponible cette semaine</p>'
        return ''.join(f'<div style="padding:7px 0;border-bottom:1px solid #f0f0f0"><a href="{u}" target="_blank" style="color:#1a3a5c;text-decoration:none;font-size:12px;line-height:1.5">→ {t}</a></div>' for u,t in arts)

    # Thèmes
    themes = [
        ('🏦 Banques & Taux BCE','La trajectoire des taux BCE détermine directement la marge nette d\'intérêt des banques. Tout discours Lagarde est un catalyseur pour BNP, ACA, GLE.','BNP · ACA · GLE','#1d4ed8','Surveiller'),
        ('⚡ Énergie & Défense','TotalEnergies bénéficie du pétrole élevé. Thales et Dassault Aviation profitent du réarmement européen (+30% budgets depuis 2022).','TTE · HO · DASSAV','#16a34a','Positif'),
        ('💊 Santé & Pharma','Novo Nordisk reste le dossier Ozempic/Wegovy. Sanofi accélère en oncologie. Virbac profite de l\'humanisation des animaux.','SAN · NOVO · VIRBAC','#16a34a','Positif'),
        ('🔧 Industrie','Schneider Electric et Legrand bénéficient de la transition énergétique. Les équipementiers auto restent sous pression.','SU · LR · VALO','#d97706','Mixte'),
    ]
    theme_html = ''
    for sector, desc, acts, col, verdict in themes:
        theme_html += f'<div style="background:#fff;border-left:3px solid {col};padding:11px 14px;margin-bottom:10px"><div style="display:flex;justify-content:space-between;margin-bottom:4px"><b style="font-size:13px">{sector}</b><span style="font-size:10px;color:{col};font-weight:700;font-family:monospace">{verdict.upper()}</span></div><p style="margin:0 0 5px;font-size:12px;color:#444;line-height:1.5">{desc}</p><div style="font-size:11px;color:#888">Actions : {acts}</div></div>'

    # Agenda
    cal = [
        ('Lundi','PMI Manufacturier EU & US','Fort — indicateur avancé activité industrie'),
        ('Mardi','Confiance consommateurs US','Moyen — baromètre conso américaine'),
        ('Mercredi','CPI Inflation Zone Euro','Fort — données BCE, impact direct sur taux'),
        ('Jeudi','Claims chômage US','Moyen — santé marché emploi'),
        ('Vendredi','NFP Emploi US','TRÈS FORT — mouvement violent possible'),
    ]
    cal_rows = ''.join(f'<tr><td style="padding:7px 12px;border-bottom:1px solid #eee;font-weight:600;font-size:12px;color:#1a3a5c;white-space:nowrap">{d}</td><td style="padding:7px 12px;border-bottom:1px solid #eee;font-size:12px">{ev}</td><td style="padding:7px 12px;border-bottom:1px solid #eee;font-size:11px;color:#666">{det}</td></tr>' for d,ev,det in cal)

    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:12px;background:#f5f3ef;font-family:Georgia,serif;color:#1a1a1a">
<div style="max-width:700px;margin:0 auto;background:#fff;box-shadow:0 2px 20px rgba(0,0,0,.08)">

<div style="background:linear-gradient(135deg,#0f2540,#1a3a5c);padding:26px 32px">
  <div style="font-family:Georgia,serif;font-size:22px;font-weight:700;color:#f0d080;letter-spacing:3px">PEA SCREENER PRO</div>
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:3px;margin-top:4px">NEWSLETTER HEBDOMADAIRE · {w}</div>
  <div style="margin-top:8px;font-size:12px;color:rgba(255,255,255,.6)">Marchés · Vos actions · Actualités · Macro · Agenda</div>
</div>

<div style="background:#f0ece0;padding:10px 32px;font-size:11px;color:#555;font-family:monospace;border-bottom:2px solid #b8860b">
SOMMAIRE : ① Marchés &nbsp;·&nbsp; ② Vos actions PEA &nbsp;·&nbsp; ③ Actualités &nbsp;·&nbsp; ④ Thèmes macro &nbsp;·&nbsp; ⑤ Agenda
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">① Marchés Mondiaux — Performance semaine</div>
  <table style="width:100%;border-collapse:collapse">
    <thead><tr style="background:#f5f3ef"><th style="padding:7px 14px;text-align:left;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Marché</th><th style="padding:7px 14px;text-align:right;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Cours</th><th style="padding:7px 14px;text-align:right;font-family:monospace;font-size:9px;color:#888;text-transform:uppercase">Semaine</th></tr></thead>
    <tbody>{mrows}</tbody>
  </table>
</div>

<div style="padding:0 32px 22px;background:#fafaf8">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">② Vos Actions PEA — Tops & Flops de la semaine</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
    <div><div style="font-family:monospace;font-size:9px;color:#16a34a;margin-bottom:8px;text-transform:uppercase">📈 Top 5 hausses</div><table style="width:100%;border-collapse:collapse">{top_rows}</table></div>
    <div><div style="font-family:monospace;font-size:9px;color:#ef4444;margin-bottom:8px;text-transform:uppercase">📉 Top 5 baisses</div><table style="width:100%;border-collapse:collapse">{bot_rows}</table></div>
  </div>
  <div style="margin-top:14px;text-align:center"><a href="https://valval73.github.io/vacances/" target="_blank" style="display:inline-block;padding:9px 22px;background:#0f2540;color:#f0d080;font-family:monospace;font-size:10px;text-decoration:none;border-radius:3px;font-weight:700;letter-spacing:1px">📊 SCREENER COMPLET →</a></div>
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:16px;border-bottom:2px solid #b8860b;padding-bottom:6px">③ Actualités Financières</div>
  <div style="margin-bottom:16px">
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">Yahoo Finance France</div>
    {art_block(art_yahoo)}
  </div>
  <div style="margin-bottom:16px">
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">Boursorama Bourse</div>
    {art_block(art_bourso)}
  </div>
  <div>
    <div style="font-family:monospace;font-size:9px;font-weight:700;color:#1a3a5c;background:#f5f3ef;padding:5px 10px;margin-bottom:8px;text-transform:uppercase">Zone Bourse</div>
    {art_block(art_zb)}
  </div>
</div>

<div style="padding:0 32px 22px;background:#fafaf8">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">④ Thèmes Macro & Sectoriels</div>
  {theme_html}
</div>

<div style="padding:22px 32px">
  <div style="font-family:monospace;font-size:9px;text-transform:uppercase;letter-spacing:3px;color:#b8860b;margin-bottom:14px;border-bottom:2px solid #b8860b;padding-bottom:6px">⑤ Agenda Macro — Semaine prochaine</div>
  <table style="width:100%;border-collapse:collapse">{cal_rows}</table>
</div>

<div style="padding:0 32px 22px">
  <div style="background:#f0ede0;border-left:3px solid #b8860b;padding:13px 15px;font-size:12px;color:#444;line-height:1.8">
    <b style="color:#1a3a5c">💡 Règles d'Or PEA Screener Pro</b><br>
    🏰 <b>MM200</b> : N'achète pas un titre en tendance baissière (cours sous MM200)<br>
    📊 <b>R/R ≥ 2x</b> : Pour 1€ risqué, exige 2€ potentiel minimum<br>
    🎯 <b>Piotroski ≥ 7 + Zone achat</b> = Signal FORT — convergence réduit le risque<br>
    ⏳ <b>PEA = horizon 5 ans</b> — La patience bat le trading actif 95% du temps
  </div>
</div>

<div style="background:#0f2540;padding:16px 32px;text-align:center">
  <div style="font-family:monospace;font-size:9px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:2px">PEA SCREENER PRO · CABINET QUANTITATIF</div>
  <div style="margin-top:4px;font-size:10px;color:rgba(255,255,255,.25)">⚠️ Document éducatif — Pas de conseil en investissement agréé AMF</div>
  <a href="https://valval73.github.io/vacances/" style="display:inline-block;margin-top:6px;color:#f0d080;font-size:11px;text-decoration:none">valval73.github.io/vacances</a>
</div>

</div></body></html>'''

def get_news():
    arts_yahoo = []
    arts_bourso = []
    arts_zb = []
    try:
        print("📰 Yahoo Finance...")
        html = urllib.request.urlopen(urllib.request.Request('https://fr.finance.yahoo.com/actualites/', headers={'User-Agent':'Mozilla/5.0','Accept-Language':'fr-FR'}), timeout=12).read().decode('utf-8','ignore')
        for link, title in re.findall(r'href="(/actualites/[^"]+)"[^>]*>([^<]{30,180})<', html)[:10]:
            title = re.sub(r'\s+',' ',title).strip()
            if len(title)>25: arts_yahoo.append(('https://fr.finance.yahoo.com'+link, title))
    except Exception as e: print(f"  Yahoo: {e}")
    try:
        print("📰 Boursorama...")
        html = urllib.request.urlopen(urllib.request.Request('https://www.boursorama.com/bourse/actualites/', headers={'User-Agent':'Mozilla/5.0'}), timeout=12).read().decode('utf-8','ignore')
        for link, title in re.findall(r'href="(/bourse/actualites/[^"]+)"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})', html)[:10]:
            title = re.sub(r'\s+',' ',title).strip()
            if len(title)>25: arts_bourso.append(('https://www.boursorama.com'+link, title))
    except Exception as e: print(f"  Boursorama: {e}")
    try:
        print("📰 Zone Bourse...")
        html = urllib.request.urlopen(urllib.request.Request('https://www.zonebourse.com/actualite-bourse/', headers={'User-Agent':'Mozilla/5.0'}), timeout=12).read().decode('utf-8','ignore')
        for link, title in re.findall(r'href="(/actualite-bourse/[^"]+)"[^>]*>\s*(?:<[^>]+>)*([^<]{30,200})', html)[:10]:
            title = re.sub(r'\s+',' ',title).strip()
            if len(title)>25: arts_zb.append(('https://www.zonebourse.com'+link, title))
    except Exception as e: print(f"  Zone Bourse: {e}")
    return arts_yahoo[:5], arts_bourso[:5], arts_zb[:5]

if __name__ == '__main__':
    print(f'📰 Newsletter {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    markets = {}
    for name, ticker in INDICES.items():
        d = fetch_yahoo(ticker)
        if d: markets[name] = d
        time.sleep(0.2)
    print(f'  → {len(markets)} marchés')
    pea = {}
    for ticker, (name, yf) in PEA_WATCHLIST.items():
        d = fetch_yahoo(yf)
        if d: pea[ticker] = {'name':name, **d}
        time.sleep(0.2)
    print(f'  → {len(pea)} actions PEA')
    ay, ab, az = get_news()
    html = build_html(markets, pea, ay, ab, az)
    if not PASSWORD:
        with open('newsletter_preview.html','w') as f: f.write(html)
        print('💾 newsletter_preview.html sauvegardé (pas de GMAIL_PASSWORD)')
    else:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'📊 PEA Pro — Hebdo {datetime.now().strftime("%d/%m/%Y")}'
        msg['From'] = SENDER; msg['To'] = RECIPIENT
        msg.attach(MIMEText(html,'html','utf-8'))
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com',465) as s:
                s.login(SENDER, PASSWORD)
                s.sendmail(SENDER, RECIPIENT, msg.as_string())
            print(f'✅ Envoyé à {RECIPIENT}')
        except Exception as e:
            print(f'❌ {e}')
