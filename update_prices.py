#!/usr/bin/env python3
"""PEA Screener - Mise a jour prix Yahoo Finance"""
import re, time, sys
from datetime import datetime
try:
    import yfinance as yf
except:
    import subprocess
    subprocess.check_call([sys.executable,"-m","pip","install","yfinance","--quiet","--break-system-packages"])
    import yfinance as yf

# Table de correspondance PEA ticker -> Yahoo Finance ticker
YAHOO = {
    "ABCA": "ABCA.PA",
    "ABIVAX": "ABVX.PA",
    "ABIVXA": "ABVX.PA",
    "AC": "AC.PA",
    "ACA": "ACA.PA",
    "ADYEN": "ADYEN.AS",
    "AF": "AF.PA",
    "AI": "AI.PA",
    "AIR": "AIR.PA",
    "AIRLQ": "AI.PA",
    "ALBIA": "ALBIA.PA",
    "ALCLF": "ALCLA.PA",
    "ALIDS": "ALIDS.PA",
    "ALMKT": "ALMKT.PA",
    "ALO": "ALO.PA",
    "ALSEI": "ALSEI.PA",
    "ALTAREA": "ALTA.PA",
    "ALTGX": "ALTX.PA",
    "ALV": "ALV.DE",
    "ARGAN": "ARG.PA",
    "ASML": "ASML.AS",
    "ATO": "ATO.PA",
    "AXA": "CS.PA",
    "BIOM": "BIM.PA",
    "BN": "BN.PA",
    "BNENF": "BEN.PA",
    "BNP": "BNP.PA",
    "BOIRON": "BOI.PA",
    "CA": "CA.PA",
    "CAP": "CAP.PA",
    "CDRCK": "CDR.PA",
    "CHSR": "CAS.PA",
    "CLASQUIN": "ALCLA.PA",
    "CNP": "CNP.PA",
    "COFA": "COFA.PA",
    "COGEFI": "COFA.PA",
    "COVIVIO": "COV.PA",
    "CSTEU": "ALCOS.PA",
    "DALET": "DLT.PA",
    "DASSAV": "AM.PA",
    "DBG": "DBG.PA",
    "DBV": "DBV.PA",
    "DERICHEBOURG": "DBG.PA",
    "DG": "DG.PA",
    "DIOR": "CDI.PA",
    "DIORCDI": "CDI.PA",
    "DSY": "DSY.PA",
    "EDENRED": "EDEN.PA",
    "EIFFAGE": "FGR.PA",
    "EL": "EL.PA",
    "ELECOR": "ELEC.PA",
    "ELIOR": "ELIOR.PA",
    "ELIS": "ELIS.PA",
    "EMEIS": "EMEIS.PA",
    "EN": "EN.PA",
    "ENGI": "ENGI.PA",
    "ENVEA": "ALENV.PA",
    "ERF": "ERF.PA",
    "ESCAP": "ALESK.PA",
    "ESKER": "ALESK.PA",
    "ESKER2": "ALESK.PA",
    "EUFSCI": "ERF.BR",
    "FGAERO": "FGA.PA",
    "FIGEAC": "FGA.PA",
    "FNAC": "FNAC.PA",
    "FNAC2": "GLVT.PA",
    "FNTS": "FPJT.PA",
    "FORVIA": "FRVIA.PA",
    "ALFPC": "ALFPC.PA",
    "FREY": "FREY.PA",
    "GALIMMO": "GALIM.PA",
    "GENIE": "GNI.PA",
    "GLE": "GLE.PA",
    "GLEVT": "GLVT.PA",
    "GTT": "GTT.PA",
    "GTTLNG": "GTT.PA",
    "HEIA": "HEIA.AS",
    "HIPAY": "HIP.PA",
    "HMS": "HMS-B.ST",
    "HMSNW": "HMS-B.ST",
    "HO": "HO.PA",
    "ICAD": "ICAD.PA",
    "IDLG": "IDL.PA",
    "IDSF": "SII.PA",
    "IMERYS": "NK.PA",
    "INTERPARFUMS": "ITP.PA",
    "INTPRF": "ITP.PA",
    "IPSEN": "IPN.PA",
    "IPSNF": "IPN.PA",
    "IPSOS": "IPS.PA",
    "ITRLN": "ITRN.SW",
    "JACMETL": "JXS.PA",
    "JACMETL2": "JXS.PA",
    "JXS": "JXS.PA",
    "KER": "KER.PA",
    "KLPI": "LI.PA",
    "KZATM": "KAP.IL",
    "LACBX": "LACR.PA",
    "LACROIX": "LACR.PA",
    "LDLC": "ALLDL.PA",
    "LDLCG": "ALLDL.PA",
    "LDLCGP": "ALLDL.PA",
    "LECTRA": "LSS.PA",
    "LEGRAND": "LR.PA",
    "LISI": "FII.PA",
    "LISI2": "FII.PA",
    "LNA": "LNA.PA",
    "LNSBN": "LNSN.PA",
    "LPE": "LPE.PA",
    "LR": "LR.PA",
    "LVMHF": "RACE.MI",
    "MANITOU": "MTU.PA",
    "MANITOU2": "MTU.PA",
    "MC": "MC.PA",
    "MERCIALYS": "MERY.PA",
    "MERY": "MRY.PA",
    "ML": "ML.PA",
    "MLAEP": "ADP.PA",
    "MLAERO": "AIR.PA",
    "MLAFF": "AF.PA",
    "MLALW": "ALLDL.PA",
    "MLARDK": "ALARK.PA",
    "MLBCF": "MLBCF.PA",
    "MLBFF": "BFF.PA",
    "MLBLT": "ALBLT.PA",
    "MLCFT": "CFT.PA",
    "MLCHG": "CAS.PA",
    "MLCMB": "MLCOB.PA",
    "MLCOB": "MLCOB.PA",
    "MLFNIV": "FNAC.PA",
    "MLGAZ": "GEI.PA",
    "MLGOM": "GLVT.PA",
    "MLHAG": "ALHAG.PA",
    "MLHRT": "ALHRT.PA",
    "MLHRZ": "ALHRZ.PA",
    "MLINS": "ALIS.PA",
    "MLJR": "ALJR.PA",
    "MLKAG": "ALKAG.PA",
    "MLLBP": "ALLBP.PA",
    "MLMCD": "ALMCD.PA",
    "MLNMG": "ALNMG.PA",
    "MLNMX": "ALNMX.PA",
    "MLNRD": "ALNRD.PA",
    "MLPFT": "PARRO.PA",
    "MLPHI": "ALPH.PA",
    "MLPSB": "ALPSB.PA",
    "MLPVR": "ALPVR.PA",
    "MLRLV": "ALRLV.PA",
    "MLSBS": "ALSBS.PA",
    "MLSMD": "ALSMD.PA",
    "MLTPX": "ALTPX.PA",
    "MLVAL": "VLU.PA",
    "MLVPN": "ALVPN.PA",
    "MLVRB": "ALVRB.PA",
    "MLXIV": "RCO.PA",
    "MLZPH": "ALZPH.PA",
    "MT": "MT.AS",
    "NAMR": "ALNAM.PA",
    "NAMREN": "ALNAM.PA",
    "NANOBT": "NANO.PA",
    "NBNTX": "NANO.PA",
    "NEXANS": "NEX.PA",
    "NEXTY": "NXI.PA",
    "NEXTY2": "NXI.PA",
    "NOVO": "NOVO-B.CO",
    "OPM": "VRLA.PA",
    "OR": "OR.PA",
    "ORA": "ORA.PA",
    "ORPEA": "ORP.PA",
    "PERNOD": "RI.PA",
    "PLASTIC": "POM.PA",
    "PLFRY": "ALPLA.PA",
    "PLUXEE": "PLX.PA",
    "PRECIA": "PREC.PA",
    "PRNRD": "RI.PA",
    "PRX": "PRX.AS",
    "PUB": "PUB.PA",
    "RADIALL": "RAL.PA",
    "RCO": "RCO.PA",
    "REXEL": "RXL.PA",
    "RI": "RI.PA",
    "RMS": "RMS.PA",
    "RNO": "RNO.PA",
    "RXLSA": "RXL.PA",
    "SAF": "SAF.PA",
    "SAMSE": "SAMS.PA",
    "SAMSE2": "SAMS.PA",
    "SAN": "SAN.PA",
    "SAP": "SAP.DE",
    "SCBSM": "ALCSC.PA",
    "SEB": "SK.PA",
    "SELENV": "SCHP.PA",
    "SEQENS": "SEQENS.PA",
    "SFCA": "WLN.PA",
    "SGO": "SGO.PA",
    "SIEMENS": "SIE.DE",
    "SIIGRP": "SII.PA",
    "SIPH": "SIPH.PA",
    "SODITECH": "ALSOC.PA",
    "SOLVB": "SOLB.BR",
    "SOP": "SOP.PA",
    "SPIE": "SPIE.PA",
    "SSYNQ": "SYENSQO.BR",
    "STEF": "STF.PA",
    "STEF2": "STF.PA",
    "STM": "STM.PA",
    "SU": "SU.PA",
    "SW": "SW.PA",
    "SYENSQO": "SYENSQO.BR",
    "TEP": "TEP.PA",
    "THERMADOR": "THEP.PA",
    "THERMD": "THEP.PA",
    "TIXEO": "ALTXO.PA",
    "TRGO": "TRI.PA",
    "TRIGANO": "TRI.PA",
    "TTE": "TTE.PA",
    "URW": "URW.AS",
    "VALO": "FR.PA",
    "VIE": "VIE.PA",
    "VIRB2": "VIRP.PA",
    "VIRBAC": "VIRP.PA",
    "VIV": "VIV.PA",
    "VK": "VK.PA",
    "VRMTX": "VMX.PA",
    "WAGA": "WAGA.PA",
    "WAGA2": "WAGA.PA",
    "WGAEN": "WAGA.PA",
    "WLN": "WLN.PA",
    "WTRGP": "ALWTR.PA",
}

def prix(yf_ticker):
    """Obtenir le prix et la variation d'un ticker Yahoo Finance"""
    for tentative in range(2):
        try:
            t = yf.Ticker(yf_ticker)
            info = t.fast_info
            p = round(float(info.last_price), 2)
            prev = round(float(info.previous_close), 2)
            if p and p > 0:
                chg = round((p - prev) / prev * 100, 2) if prev else 0
                return p, chg
        except:
            pass
        try:
            h = yf.Ticker(yf_ticker).history(period="2d")
            if len(h) >= 2:
                p = round(float(h["Close"].iloc[-1]), 2)
                prev = round(float(h["Close"].iloc[-2]), 2)
                chg = round((p - prev) / prev * 100, 2) if prev else 0
                return p, chg
        except:
            pass
        time.sleep(0.5)
    return None, None

def maj_html(resultats):
    """Mettre a jour les prix dans index.html"""
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    mis_a_jour = 0
    for ticker, (p, chg) in resultats.items():
        if not p or p <= 0:
            continue
        # Pattern simple et robuste
        avant = "ticker:'" + ticker + "'"
        if avant not in html:
            continue
        # Remplacer price:XXXXX,chg:YYYYY apres le ticker
        pattern = "(" + re.escape(avant) + r"[^{]{0,200}?price:)[\d.]+?(,chg:)[-\d.]+"
        nouveau, n = re.subn(pattern, r"\g<1>" + str(p) + r"\g<2>" + str(chg), html, flags=re.DOTALL)
        if n > 0:
            html = nouveau
            mis_a_jour += 1
            print(f"  OK {ticker}: {p}e ({chg:+.2f}%)")
        else:
            print(f"  ?? {ticker}: prix={p} mais pattern non trouve")
    
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    html = re.sub(r"Donnees indicatives|Mis a jour [\d/]+ [\d:]+",
                  "Mis a jour " + ts, html, count=1)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\nTotal mis a jour: {mis_a_jour}/{len(resultats)} - {ts}")
    return mis_a_jour

if __name__ == "__main__":
    print("=" * 50)
    print(f"PEA Screener Prix - {len(YAHOO)} tickers")
    print(f"Debut: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 50)
    
    resultats = {}
    erreurs = 0
    for i, (pea, yf_t) in enumerate(YAHOO.items(), 1):
        sys.stdout.write(f"[{i:3d}/{len(YAHOO)}] {pea:12s} ({yf_t:15s}) ")
        sys.stdout.flush()
        p, chg = prix(yf_t)
        if p:
            print(f"-> {p}e ({chg:+.2f}%)")
        else:
            print("-> ECHEC Yahoo")
            erreurs += 1
        resultats[pea] = (p, chg)
        time.sleep(0.15)
    
    print(f"\nYahoo: {len(YAHOO)-erreurs}/{len(YAHOO)} OK, {erreurs} echecs")
    maj_html(resultats)
    print("Termine!")
