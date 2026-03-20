#!/usr/bin/env python3
"""PEA Screener Pro - Mise a jour automatique via yfinance"""
import re, time, sys
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "--quiet"])
    import yfinance as yf

YAHOO_MAP = {
    # ═══ CAC 40 ═══
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
    # ═══ SBF 120 ═══
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
    "LACROIX":"LACR.PA","LDLC":"ALLDL.PA","REXEL":"RXL.PA",
    "NEXTY":"NXI.PA","MANITOU":"MTU.PA","JACMETL":"JXS.PA",
    "SAMSE":"SAMS.PA","LISI":"FII.PA","IPSEN":"IPN.PA",
    "MERCIALYS":"MERY.PA","MLVAL":"VLU.PA","NAMR":"ALNAM.PA",
    "SEQENS":"SEQENS.PA","ELECOR":"ELEC.PA","FNAC2":"GLVT.PA",
    "PERNOD":"RI.PA","DIOR":"CDI.PA",
    # ═══ Sessions ajoutées ═══
    "ABIVAX":"ABVX.PA","NANOBT":"NANO.PA","ICAD":"ICAD.PA",
    "VRMTX":"VMX.PA","DBV":"DBV.PA","HIPAY":"HIP.PA","TIXEO":"ALTXO.PA",
    "LISI2":"FII.PA","WAGA2":"WAGA.PA","FIGEAC":"FGA.PA","LDLCG":"ALLDL.PA",
    "NAMREN":"ALNAM.PA","ESCAP":"ALESK.PA","ESKER2":"ALESK.PA",
    "SCBSM":"ALCSC.PA","SIIGRP":"SII.PA","ENVEA":"ALENV.PA",
    "EMEIS":"EMEIS.PA","FPJT":"FPJT.PA","SELENV":"SCHP.PA",
    "ALBIA":"ALBIA.PA","LACBX":"LACR.PA","KZATM":"KAP.IL",
    "DALET":"DLT.PA","LNSBN":"LNSN.PA","ALTGX":"ALTX.PA",
    "ITRLN":"ITRN.SW","MLAEP":"ADP.PA","MLCHG":"CAS.PA",
    "MLFNIV":"FNAC.PA","GTTLNG":"GTT.PA","AIRLQ":"AI.PA",
    "DIORCDI":"CDI.PA","ABIVXA":"ABVX.PA","NBNTX":"NANO.PA",
    "WTRGP":"ALWTR.PA","TRGO":"TRI.PA","BNENF":"BEN.PA",
    "LDLCGP":"ALLDL.PA","WGAEN":"WAGA.PA","PRNRD":"RI.PA",
    "RXLSA":"RXL.PA","FGAERO":"FGA.PA","SSYNQ":"SYENSQO.BR",
    "SOLVB":"SOLB.BR","IPSNF":"IPN.PA","THERMD":"THEP.PA",
    "VIRB2":"VIRP.PA","INTPRF":"ITP.PA","STEF2":"STF.PA",
    "SODITECH":"ALSOC.PA","ALIDS":"ALIDS.PA",
    "EUFSCI":"ERF.BR","MLPFT":"PARRO.PA","CSTEU":"ALCOS.PA",
    # ═══ Européennes éligibles PEA ═══
    "ASML":"ASML.AS","PRX":"PRX.AS","ADYEN":"ADYEN.AS","HEIA":"HEIA.AS",
    "NOVO":"NOVO-B.CO","SAP":"SAP.DE","SIEMENS":"SIE.DE","ALV":"ALV.DE",
    "LVMHF":"RACE.MI","HMS":"HMS-B.ST","RADIALL":"RAL.PA",
    "HMSNW":"HMS-B.ST","JACMETL2":"JXS.PA","SAMSE2":"SAMS.PA",
    "MANITOU2":"MTU.PA","NEXTY2":"NXI.PA",

    # ═══ Complément mappings ═══
    "ALCLF":"ALCLA.PA",
    "ALMKT":"ALMKT.PA",
    "ALSEI":"ALSEI.PA",
    "CDRCK":"CDR.PA",
    "COGEFI":"COFA.PA",
    "DBG":"DBG.PA",
    "GALIMMO":"GALIM.PA",
    "GENIE":"GNI.PA",
    "GLEVT":"GLVT.PA",
    "IDSF":"SII.PA",
    "LEGRAND":"LR.PA",
    "LPE":"LPE.PA",
    "MLAERO":"AIR.PA",
    "MLAFF":"AF.PA",
    "MLALW":"ALLDL.PA",
    "MLARDK":"ALARK.PA",
    "MLBCF":"MLBCF.PA",
    "MLBFF":"BFF.PA",
    "MLBLT":"ALBLT.PA",
    "MLCFT":"CFT.PA",
    "MLCMB":"MLCOB.PA",
    "MLCOB":"MLCOB.PA",
    "MLGAZ":"GEI.PA",
    "MLHAG":"ALHAG.PA",
    "MLHRT":"ALHRT.PA",
    "MLHRZ":"ALHRZ.PA",
    "MLINS":"ALIS.PA",
    "MLJR":"ALJR.PA",
    "MLKAG":"ALKAG.PA",
    "MLLBP":"ALLBP.PA",
    "MLMCD":"ALMCD.PA",
    "MLNMG":"ALNMG.PA",
    "MLNMX":"ALNMX.PA",
    "MLNRD":"ALNRD.PA",
    "MLPSB":"ALPSB.PA",
    "MLPVR":"ALPVR.PA",
    "MLRLV":"ALRLV.PA",
    "MLSBS":"ALSBS.PA",
    "MLSMD":"ALSMD.PA",
    "MLTPX":"ALTPX.PA",
    "MLVPN":"ALVPN.PA",
    "MLVRB":"ALVRB.PA",
    "MLXIV":"RCO.PA",
    "MLZPH":"ALZPH.PA",
    "ORPEA":"ORP.PA",
    "SFCA":"WLN.PA",
    "PRECIA":"PREC.PA",

    "MLGOM":"GLVT.PA",
    "MLPHI":"ALPH.PA",
    "PLFRY":"ALPLA.PA",
    "SYENSQO":"SYENSQO.BR",
}

def get_price(yf_ticker):
    """Prix via yfinance avec fallback history"""
    try:
        t = yf.Ticker(yf_ticker)
        info = t.fast_info
        price = round(float(info.last_price), 2)
        prev = round(float(info.previous_close), 2)
        chg = round((price - prev) / prev * 100, 2) if prev else 0
        if price > 0:
            return price, chg
    except:
        pass
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
    skipped = 0
    for ticker, (price, chg) in prices.items():
        if not price or price <= 0:
            skipped += 1
            continue
        # Pattern: matches ticker:'TICKER' ... price:123.45,chg:
        pat = "(ticker:'" + re.escape(ticker) + r"'[^{]*?price:)[\d.]+?(,chg:)[-\d.]+"
        new_content, n = re.subn(pat, r"\g<1>" + str(price) + r"\g<2>" + str(chg), 
                                  content, flags=re.DOTALL)
        if n > 0:
            content = new_content
            updated += 1
            print(f"  OK {ticker}: {price} ({chg:+.2f}%)")
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    content = re.sub(
        "(Donnees indicatives|Mis a jour [0-9]+/[0-9]+/[0-9]+ [0-9]+:[0-9]+)",
        f"Mis a jour {ts}", content, count=1
    )
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\nTotal: {updated}/{len(prices)} mis a jour ({skipped} echecs Yahoo) - {ts}")
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
