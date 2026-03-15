#!/usr/bin/env python3
"""PEA Screener Pro - Mise à jour automatique des prix via GitHub Actions"""
import json, re, time, urllib.request
from datetime import datetime

YAHOO_MAP = {
    # CAC 40 complet
    'MC':'MC.PA','AI':'AI.PA','OR':'OR.PA','RMS':'RMS.PA','SAN':'SAN.PA',
    'TTE':'TTE.PA','SAF':'SAF.PA','SU':'SU.PA','AXA':'CS.PA','BNP':'BNP.PA',
    'ACA':'ACA.PA','GLE':'GLE.PA','AIR':'AIR.PA','KER':'KER.PA','PUB':'PUB.PA',
    'ORA':'ORA.PA','VIE':'VIE.PA','RNO':'RNO.PA','SGO':'SGO.PA','CAP':'CAP.PA',
    'DG':'DG.PA','VIV':'VIV.PA','RI':'RI.PA','LR':'LR.PA','WLN':'WLN.PA',
    'DSY':'DSY.PA','STM':'STM.PA','EL':'EL.PA','ML':'ML.PA','ENGI':'ENGI.PA',
    'MT':'MT.AS','URW':'URW.AS','SW':'SW.PA','TEP':'TEP.PA','EN':'EN.PA',
    'AC':'AC.PA','AF':'AF.PA','BN':'BN.PA','CA':'CA.PA','HO':'HO.PA',
    'ATO':'ATO.PA','EIFFAGE':'FGR.PA','EDENRED':'EDEN.PA',
    'VALO':'FR.PA','FORVIA':'FRVIA.PA',
    # SBF 120
    'GTT':'GTT.PA','COFA':'COFA.PA','MERY':'MRY.PA','JXS':'JXS.PA',
    'SPIE':'SPIE.PA','NEXANS':'NEX.PA','DASSAV':'AM.PA','ALO':'ALO.PA',
    'ELIS':'ELIS.PA','SEB':'SK.PA','ERF':'ERF.PA','IPSOS':'IPS.PA',
    'ABCA':'ABCA.PA','VK':'VK.PA','FNAC':'FNAC.PA','LNA':'LNA.PA',
    'CNP':'CNP.PA','SOP':'SOP.PA','BIOM':'BIM.PA','KLPI':'LI.PA',
    'RCO':'RCO.PA','ALTAREA':'ALTA.PA','COVIVIO':'COV.PA','FREY':'FREY.PA',
    'FNTS':'FPJT.PA','TRIGANO':'TRI.PA','BOIRON':'BOI.PA','CHSR':'CAS.PA',
    'PLASTIC':'POM.PA','SIPH':'SIPH.PA','PLUXEE':'PLX.PA','OPM':'VRLA.PA',
    'DERICHEBOURG':'DBG.PA','SFCA':'WLN.PA',
    # Européennes éligibles PEA
    'ASML':'ASML.AS','PRX':'PRX.AS','ADYEN':'ADYEN.AS','HEIA':'HEIA.AS',
    'NOVO':'NOVO-B.CO','SAP':'SAP.DE','SIEMENS':'SIE.DE','ALV':'ALV.DE',
    'LVMHF':'RACE.MI',
}

def get_price(ticker_yahoo):
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker_yahoo}?interval=1d&range=1d'
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        meta = data['chart']['result'][0]['meta']
        price = round(meta.get('regularMarketPrice', 0), 2)
        prev = meta.get('previousClose', price)
        chg = round((price - prev) / prev * 100, 2) if prev else 0
        return price, chg
    except Exception as e:
        print(f'  ⚠️  {ticker_yahoo}: {e}')
        return None, None

def update_html(prices):
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    updated = 0
    for ticker, (price, chg) in prices.items():
        if not price or price <= 0: continue
        pattern = rf"(ticker:'{re.escape(ticker)}'[^{{]*?price:)[\d.]+?(,chg:)[-\d.]+"
        new_content, n = re.subn(pattern, rf'\g<1>{price}\g<2>{chg}', content, flags=re.DOTALL)
        if n > 0:
            content = new_content
            updated += 1
            print(f'  ✅ {ticker}: {price}€ ({chg:+.2f}%)')
    ts = datetime.now().strftime('%d/%m/%Y %H:%M')
    content = re.sub(r'(Données indicatives|Mis à jour \d{2}/\d{2}/\d{4} \d{2}:\d{2})', f'Mis à jour {ts}', content, count=1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'\n✅ {updated} cours mis à jour — {ts}')

if __name__ == '__main__':
    print(f'🔄 PEA Screener — {len(YAHOO_MAP)} tickers — {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    prices = {}
    for i, (t, yf) in enumerate(YAHOO_MAP.items(), 1):
        print(f'[{i:02d}/{len(YAHOO_MAP)}] {t} ({yf})')
        prices[t] = get_price(yf)
        time.sleep(0.3)
    update_html(prices)
    print('🎉 Terminé!')
