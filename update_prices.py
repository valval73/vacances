#!/usr/bin/env python3
"""
PEA Screener Pro - Mise à jour automatique des prix
Tourne chaque matin à 7h (lundi-vendredi) via GitHub Actions
Récupère les prix sur Yahoo Finance et met à jour index.html
"""
import json, re, time, urllib.request
from datetime import datetime

# Map ticker PEA -> ticker Yahoo Finance
YAHOO_MAP = {
    'MC':'MC.PA','AI':'AI.PA','OR':'OR.PA','RMS':'RMS.PA','SAN':'SAN.PA',
    'TTE':'TTE.PA','SAF':'SAF.PA','SU':'SU.PA','AXA':'CS.PA','BNP':'BNP.PA',
    'ACA':'ACA.PA','GLE':'GLE.PA','AIR':'AIR.PA','KER':'KER.PA','PUB':'PUB.PA',
    'ORA':'ORA.PA','VIE':'VIE.PA','RNO':'RNO.PA','SGO':'SGO.PA','CAP':'CAP.PA',
    'DG':'DG.PA','VIV':'VIV.PA','RI':'RI.PA','LR':'LR.PA','WLN':'WLN.PA',
    'DSY':'DSY.PA','STM':'STM.PA','EL':'EL.PA','ML':'ML.PA','ENGI':'ENGI.PA',
    'MT':'MT.AS','URW':'URW.AS','SW':'SW.PA','TEP':'TEP.PA','EN':'EN.PA',
    'GTT':'GTT.PA','COFA':'COFA.PA','MERY':'MRY.PA','JXS':'JXS.PA',
    'SPIE':'SPIE.PA','NEXANS':'NEX.PA','DASSAV':'AM.PA','ALO':'ALO.PA',
    'ELIS':'ELIS.PA','SEB':'SK.PA','ERF':'ERF.PA','IPSOS':'IPS.PA',
    'ABCA':'ABCA.PA','VK':'VK.PA','FNAC':'FNAC.PA','LNA':'LNA.PA',
    'CNP':'CNP.PA','SOP':'SOP.PA',
}

def get_price(ticker_yahoo):
    """Récupère le cours et variation depuis Yahoo Finance"""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker_yahoo}?interval=1d&range=1d'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta = data['chart']['result'][0]['meta']
        price = round(meta.get('regularMarketPrice', 0), 2)
        prev = meta.get('previousClose', price)
        chg = round((price - prev) / prev * 100, 2) if prev else 0
        return price, chg
    except Exception as e:
        print(f'  ⚠️  Erreur {ticker_yahoo}: {e}')
        return None, None

def update_html(prices):
    """Met à jour les prix dans index.html"""
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    updated = 0
    for ticker, (price, chg) in prices.items():
        if price is None or price <= 0:
            continue
        pattern = rf"(ticker:'{re.escape(ticker)}'[^{{]*?price:)[\d.]+?(,chg:)[-\d.]+"
        replacement = rf'\g<1>{price}\g<2>{chg}'
        new_content, n = re.subn(pattern, replacement, content, flags=re.DOTALL)
        if n > 0:
            content = new_content
            updated += 1
            print(f'  ✅ {ticker}: {price}€ ({chg:+.2f}%)')
        else:
            print(f'  ⚠️  {ticker}: pattern non trouvé dans index.html')

    # Mettre à jour le timestamp dans le header
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    content = re.sub(r'(Données indicatives|Mis à jour \d{2}/\d{2}/\d{4} \d{2}:\d{2})',
                     f'Mis à jour {ts}', content, count=1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'\n✅ {updated}/{len(prices)} cours mis à jour — {ts}')
    return updated

if __name__ == '__main__':
    print('🔄 PEA Screener Pro — Mise à jour des cours')
    print(f'📅 {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    print(f'📊 {len(YAHOO_MAP)} actions à mettre à jour\n')

    prices = {}
    for i, (pea_ticker, yahoo_ticker) in enumerate(YAHOO_MAP.items(), 1):
        print(f'[{i:02d}/{len(YAHOO_MAP)}] Récupération {pea_ticker} ({yahoo_ticker})...')
        price, chg = get_price(yahoo_ticker)
        prices[pea_ticker] = (price, chg)
        time.sleep(0.4)  # éviter le rate limiting Yahoo

    print('\n--- Mise à jour index.html ---')
    update_html(prices)
    print('\n🎉 Terminé! Le screener est à jour.')
