#!/usr/bin/env python3
"""PEA Screener Pro - Mise a jour automatique via yfinance - 220 tickers"""
import re, time, sys
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "--quiet"])
    import yfinance as yf

YAHOO_MAP = {
    "ABCA":"ABCA.PA",
    "ABIVAX":"ABVX.PA",
    "ABIVXA":"ABVX.PA",
    "AC":"AC.PA",
    "ACA":"ACA.PA",
    "ADYEN":"ADYEN.AS",
    "AF":"AF.PA",
    "AI":"AI.PA",
    "AIR":"AIR.PA",
    "AIRLQ":"AI.PA",
    "ALBIA":"ALBIA.PA",
    "ALCLF":"ALCLA.PA",
    "ALIDS":"ALIDS.PA",
    "ALMKT":"ALMKT.PA",
    "ALO":"ALO.PA",
    "ALSEI":"ALSEI.PA",
    "ALTAREA":"ALTA.PA",
    "ALTGX":"ALTX.PA",
    "ALV":"ALV.DE",
    "ARGAN":"ARG.PA",
    "ASML":"ASML.AS",
    "ATO":"ATO.PA",
    "AXA":"CS.PA",
    "BIOM":"BIM.PA",
    "BN":"BN.PA",
    "BNENF":"BEN.PA",
    "BNP":"BNP.PA",
    "BOIRON":"BOI.PA",
    "CA":"CA.PA",
    "CAP":"CAP.PA",
    "CDRCK":"CDR.PA",
    "CHSR":"CAS.PA",
    "CLASQUIN":"ALCLA.PA",
    "CNP":"CNP.PA",
    "COFA":"COFA.PA",
    "COGEFI":"COFA.PA",
    "COVIVIO":"COV.PA",
    "CSTEU":"ALCOS.PA",
    "DALET":"DLT.PA",
    "DASSAV":"AM.PA",
    "DBG":"DBG.PA",
    "DBV":"DBV.PA",
    "DERICHEBOURG":"DBG.PA",
    "DG":"DG.PA",
    "DIOR":"CDI.PA",
    "DIORCDI":"CDI.PA",
    "DSY":"DSY.PA",
    "EDENRED":"EDEN.PA",
    "EIFFAGE":"FGR.PA",
    "EL":"EL.PA",
    "ELECOR":"ELEC.PA",
    "ELIOR":"ELIOR.PA",
    "ELIS":"ELIS.PA",
    "EMEIS":"EMEIS.PA",
    "EN":"EN.PA",
    "ENGI":"ENGI.PA",
    "ENVEA":"ALENV.PA",
    "ERF":"ERF.PA",
    "ESCAP":"ALESK.PA",
    "ESKER":"ALESK.PA",
    "EUFSCI":"ERF.BR",
    "FGAERO":"FGA.PA",
    "FIGEAC":"FGA.PA",
    "FNAC":"FNAC.PA",
    "FNTS":"FPJT.PA",
    "FORVIA":"FRVIA.PA",
    "FPJT":"FPJT.PA",
    "FREY":"FREY.PA",
    "GALIMMO":"GALIM.PA",
    "GENIE":"GNI.PA",
    "GLE":"GLE.PA",
    "GLEVT":"GLVT.PA",
    "GTT":"GTT.PA",
    "GTTLNG":"GTT.PA",
    "HEIA":"HEIA.AS",
    "HIPAY":"HIP.PA",
    "HMSNW":"HMS-B.ST",
    "HO":"HO.PA",
    "ICAD":"ICAD.PA",
    "IDLG":"IDL.PA",
    "IDSF":"ALIDS.PA",
    "IMERYS":"NK.PA",
    "INTERPARFUMS":"ITP.PA",
    "INTPRF":"ITP.PA",
    "IPSEN":"IPN.PA",
    "IPSNF":"IPN.PA",
    "IPSOS":"IPS.PA",
    "ITRLN":"ITRN.SW",
    "JACMETL":"JXS.PA",
    "JXS":"JXS.PA",
    "KER":"KER.PA",
    "KLPI":"LI.PA",
    "KZATM":"KAP.IL",
    "LACBX":"LACR.PA",
    "LACROIX":"LACR.PA",
    "LDLC":"ALLDL.PA",
    "LDLCG":"ALLDL.PA",
    "LECTRA":"LSS.PA",
    "LEGRAND":"LR.PA",
    "LISI":"FII.PA",
    "LNA":"LNA.PA",
    "LNSBN":"LNSN.PA",
    "LPE":"LPE.PA",
    "LR":"LR.PA",
    "LVMHF":"RACE.MI",
    "MANITOU":"MTU.PA",
    "MC":"MC.PA",
    "MERCIALYS":"MERY.PA",
    "MERY":"MRY.PA",
    "ML":"ML.PA",
    "MLAEP":"ADP.PA",
    "MLAERO":"AIR.PA",
    "MLAFF":"AFF.PA",
    "MLALW":"ALOW.PA",
    "MLARDK":"ALARK.PA",
    "MLBCF":"MLBCF.PA",
    "MLBFF":"BFF.PA",
    "MLBLT":"ALBLT.PA",
    "MLCFT":"CFT.PA",
    "MLCHG":"CAS.PA",
    "MLCOB":"COBS.PA",
    "MLFNIV":"FNAC.PA",
    "MLGAZ":"GEI.PA",
    "MLGOM":"GLVT.PA",
    "MLHAG":"ALHAG.PA",
    "MLHRT":"ALHRT.PA",
    "MLHRZ":"ALHRZ.PA",
    "MLINS":"ALIS.PA",
    "MLJR":"ALJR.PA",
    "MLKAG":"ALKAG.PA",
    "MLLBP":"ALLBP.PA",
    "MLMCD":"ALMCD.PA",
    "MLNMG":"MLNMG.PA",
    "MLNMX":"ALNMX.PA",
    "MLNRD":"ALNRD.PA",
    "MLPFT":"PARRO.PA",
    "MLPHI":"ALPH.PA",
    "MLPSB":"ALPSB.PA",
    "MLPVR":"ALPVR.PA",
    "MLRLV":"ALRLV.PA",
    "MLSBS":"ALSBS.PA",
    "MLSMD":"ALSMD.PA",
    "MLTPX":"ALTPX.PA",
    "MLVAL":"VLU.PA",
    "MLVPN":"ALVPN.PA",
    "MLVRB":"ALVRB.PA",
    "MLXIV":"RCO.PA",
    "MLZPH":"ALZPH.PA",
    "MT":"MT.AS",
    "NAMR":"ALNAM.PA",
    "NAMREN":"ALNAM.PA",
    "NANOBT":"NANO.PA",
    "NBNTX":"NANO.PA",
    "NEXANS":"NEX.PA",
    "NEXTY":"NXI.PA",
    "NOVO":"NOVO-B.CO",
    "OPM":"VRLA.PA",
    "OR":"OR.PA",
    "ORA":"ORA.PA",
    "ORPEA":"ORP.PA",
    "PERNOD":"RI.PA",
    "PLASTIC":"POM.PA",
    "PLFRY":"ALPLA.PA",
    "PLUXEE":"PLX.PA",
    "PRECIA":"PREC.PA",
    "PRNRD":"RI.PA",
    "PRX":"PRX.AS",
    "PUB":"PUB.PA",
    "RADIALL":"RAL.PA",
    "RCO":"RCO.PA",
    "REXEL":"RXL.PA",
    "RI":"RI.PA",
    "RMS":"RMS.PA",
    "RNO":"RNO.PA",
    "RXLSA":"RXL.PA",
    "SAF":"SAF.PA",
    "SAMSE":"SAMS.PA",
    "SAN":"SAN.PA",
    "SAP":"SAP.DE",
    "SCBSM":"ALCSC.PA",
    "SEB":"SK.PA",
    "SELENV":"SCHP.PA",
    "SEQENS":"SEQENS.PA",
    "SFCA":"WLN.PA",
    "SGO":"SGO.PA",
    "SIEMENS":"SIE.DE",
    "SIIGRP":"SII.PA",
    "SIPH":"SIPH.PA",
    "SODITECH":"ALSOC.PA",
    "SOLVAY":"SOLB.BR",
    "SOLVB":"SOLB.BR",
    "SOP":"SOP.PA",
    "SPIE":"SPIE.PA",
    "SSYNQ":"SYENSQO.BR",
    "STEF":"STF.PA",
    "STEF2":"STF.PA",
    "STM":"STM.PA",
    "SU":"SU.PA",
    "SW":"SW.PA",
    "SYENSQO":"SYENSQO.BR",
    "SYENSQO2":"SYENSQO.BR",
    "TEP":"TEP.PA",
    "THERMADOR":"THEP.PA",
    "THERMD":"THEP.PA",
    "TIXEO":"ALTXO.PA",
    "TRGO":"TRI.PA",
    "TRIGANO":"TRI.PA",
    "TTE":"TTE.PA",
    "URW":"URW.AS",
    "VALO":"FR.PA",
    "VIE":"VIE.PA",
    "VIRB2":"VIRP.PA",
    "VIRBAC":"VIRP.PA",
    "VIV":"VIV.PA",
    "VK":"VK.PA",
    "VRMTX":"VMX.PA",
    "WAGA":"WAGA.PA",
    "WGAEN":"WAGA.PA",
    "WLN":"WLN.PA",
    "WTRGP":"ALWTR.PA",
}

def get_price(yf_ticker):
    try:
        t = yf.Ticker(yf_ticker)
        info = t.fast_info
        price = round(float(info.last_price), 2)
        prev = round(float(info.previous_close), 2)
        chg = round((price - prev) / prev * 100, 2) if prev else 0
        return price, chg
    except:
        try:
            hist = yf.Ticker(yf_ticker).history(period="2d")
            if len(hist) >= 2:
                price = round(float(hist["Close"].iloc[-1]), 2)
                prev = round(float(hist["Close"].iloc[-2]), 2)
                chg = round((price - prev) / prev * 100, 2) if prev else 0
                return price, chg
        except:
            pass
        return None, None

def update_html(prices):
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    updated = 0
    for ticker, (price, chg) in prices.items():
        if not price or price <= 0:
            continue
        pattern = rf"(ticker:\'{re.escape(ticker)}\'[^{{]*?price:)[\d.]+?(,chg:)[-\d.]+"
        new_content, n = re.subn(pattern, rf"\g<1>{price}\g<2>{chg}", content, flags=re.DOTALL)
        if n > 0:
            content = new_content
            updated += 1
            print(f"  OK {ticker}: {price} ({chg:+.2f}%)")
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    content = re.sub(r"(Donnees indicatives|Mis a jour [0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+)",
                     f"Mis a jour {ts}", content, count=1)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nTotal: {updated}/{len(prices)} mis a jour - {ts}")
    return updated

if __name__ == "__main__":
    print("PEA Screener - " + str(len(YAHOO_MAP)) + " tickers - " + datetime.now().strftime("%d/%m/%Y %H:%M"))
    prices = {}
    for i, (pea, yf_t) in enumerate(YAHOO_MAP.items(), 1):
        print(f"[{i:02d}/{len(YAHOO_MAP)}] {pea} ({yf_t})")
        p, ch = get_price(yf_t)
        prices[pea] = (p, ch)
        time.sleep(0.1)
    update_html(prices)
    print("Termine!")
