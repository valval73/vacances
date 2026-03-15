#!/usr/bin/env python3
"""PEA Screener Pro - Mise a jour automatique des prix
SOLUTION: yfinance library (bypass Yahoo blocks sur GitHub Actions)
"""
import re, time, sys
from datetime import datetime

# Install yfinance if not present
try:
    import yfinance as yf
    print("yfinance OK")
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "--quiet"])
    import yfinance as yf
    print("yfinance installe")

YAHOO_MAP = {
    # CAC 40
    "MC":"MC.PA","AI":"AI.PA","OR":"OR.PA","RMS":"RMS.PA","SAN":"SAN.PA",
    "TTE":"TTE.PA","SAF":"SAF.PA","SU":"SU.PA","AXA":"CS.PA","BNP":"BNP.PA",
    "ACA":"ACA.PA","GLE":"GLE.PA","AIR":"AIR.PA","KER":"KER.PA","PUB":"PUB.PA",
    "ORA":"ORA.PA","VIE":"VIE.PA","RNO":"RNO.PA","SGO":"SGO.PA","CAP":"CAP.PA",
    "DG":"DG.PA","VIV":"VIV.PA","RI":"RI.PA","LR":"LR.PA","WLN":"WLN.PA",
    "DSY":"DSY.PA","STM":"STM.PA","EL":"EL.PA","ML":"ML.PA","ENGI":"ENGI.PA",
    "MT":"MT.AS","URW":"URW.AS","SW":"SW.PA","TEP":"TEP.PA","EN":"EN.PA",
    "AC":"AC.PA","AF":"AF.PA","BN":"BN.PA","CA":"CA.PA","HO":"HO.PA",
    "ATO":"ATO.PA","EIFFAGE":"FGR.PA","EDENRED":"EDEN.PA",
    "VALO":"FR.PA","FORVIA":"FRVIA.PA",
    # SBF 120 + SRD
    "GTT":"GTT.PA","COFA":"COFA.PA","MERY":"MRY.PA","JXS":"JXS.PA",
    "SPIE":"SPIE.PA","NEXANS":"NEX.PA","DASSAV":"AM.PA","ALO":"ALO.PA",
    "ELIS":"ELIS.PA","SEB":"SK.PA","ERF":"ERF.PA","IPSOS":"IPS.PA",
    "ABCA":"ABCA.PA","VK":"VK.PA","FNAC":"FNAC.PA","LNA":"LNA.PA",
    "CNP":"CNP.PA","SOP":"SOP.PA","BIOM":"BIM.PA","KLPI":"LI.PA",
    "RCO":"RCO.PA","ALTAREA":"ALTA.PA","COVIVIO":"COV.PA","FREY":"FREY.PA",
    "FNTS":"FPJT.PA","TRIGANO":"TRI.PA","BOIRON":"BOI.PA","CHSR":"CAS.PA",
    "PLASTIC":"POM.PA","SIPH":"SIPH.PA","PLUXEE":"PLX.PA","OPM":"VRLA.PA",
    "DERICHEBOURG":"DBG.PA","IMERYS":"NK.PA","THERMADOR":"THEP.PA",
    "STEF":"STF.PA","VIRBAC":"VIRP.PA","INTERPARFUMS":"ITP.PA",
    "CLASQUIN":"ALCLA.PA","ARGAN":"ARG.PA","ESKER":"ALESK.PA",
    "LECTRA":"LSS.PA","IDLG":"IDL.PA","ELIOR":"ELIOR.PA","WAGA":"WAGA.PA",
    "LACROIX":"LACR.PA","SEQENS":"SEQENS.PA","LDLC":"ALLDL.PA",
    # Europeennes PEA
    "ASML":"ASML.AS","PRX":"PRX.AS","ADYEN":"ADYEN.AS","HEIA":"HEIA.AS",
    "NOVO":"NOVO-B.CO","SAP":"SAP.DE","SIEMENS":"SIE.DE","ALV":"ALV.DE",
    "LVMHF":"RACE.MI",
}

def get_price_yf(ticker_yf):
    """Recupere prix via yfinance - beaucoup plus fiable que l API brute"""
    try:
        t = yf.Ticker(ticker_yf)
        info = t.fast_info
        price = round(float(info.last_price), 2)
        prev = round(float(info.previous_close), 2)
        chg = round((price - prev) / prev * 100, 2) if prev else 0
        return price, chg
    except Exception as e:
        # Fallback: history
        try:
            hist = yf.Ticker(ticker_yf).history(period="2d")
            if len(hist) >= 2:
                price = round(float(hist["Close"].iloc[-1]), 2)
                prev = round(float(hist["Close"].iloc[-2]), 2)
                chg = round((price - prev) / prev * 100, 2) if prev else 0
                return price, chg
        except:
            pass
        print(f"  ERR {ticker_yf}: {e}")
        return None, None

def update_html(prices):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    updated = 0
    for ticker, (price, chg) in prices.items():
        if not price or price <= 0:
            continue
        pattern = rf"(ticker:'{re.escape(ticker)}'[^{{]*?price:)[\d.]+?(,chg:)[-\d.]+"
        new_content, n = re.subn(pattern, rf"\g<1>{price}\g<2>{chg}", content, flags=re.DOTALL)
        if n > 0:
            content = new_content
            updated += 1
            print(f"  OK {ticker}: {price} ({chg:+.2f}%)")
        else:
            print(f"  SKIP {ticker}: pattern non trouve")
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    content = re.sub(
        r"(Donnees indicatives|Mis a jour \d{2}/\d{2}/\d{4} \d{2}:\d{2})",
        f"Mis a jour {ts}", content, count=1
    )
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nTotal: {updated}/{len(prices)} mis a jour - {ts}")
    return updated

if __name__ == "__main__":
    print(f"PEA Screener - Mise a jour prix - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{len(YAHOO_MAP)} tickers\n")
    prices = {}
    for i, (pea, yf_ticker) in enumerate(YAHOO_MAP.items(), 1):
        print(f"[{i:02d}/{len(YAHOO_MAP)}] {pea} ({yf_ticker})")
        p, c = get_price_yf(yf_ticker)
        prices[pea] = (p, c)
        time.sleep(0.1)  # yfinance est plus rapide
    print("\n--- Update index.html ---")
    update_html(prices)
    print("\nTermine!")
