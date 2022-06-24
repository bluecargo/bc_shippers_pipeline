from collections import defaultdict
import django
import os
import requests
import csv
import time
import os
import json
import tqdm
from dotenv import dotenv_values
import random
import pandas as pd

config = dotenv_values(".env")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

SCAC_PER_TERMINAL = {
    "tti": ['CMLF', 'JCTK', 'PARB', 'KFKC', 'ADXH', 'SGAT', 'ROLY', 'TIKG', 'MHBQ', 'KTEV', 'PSED', 'TGSM', 'JDLC', 'YMLU', 'MXDP', 'AQEG', 'HKTH', 'BOLS', 'PACL', 'SNEA', 'OSGB', 'EGHC', 'DEUC', 'DWCH', 'AANA', 'USON', 'CFMM', 'NOTQ', 'NGLN', 'ISNC', 'RLUP', 'CCOO', 'CVDG', 'TRUO', 'WLGO', 'DPHE', 'CPTD', 'TCED', 'EOIA', 'RTIB', 'CGLQ', 'KCNT', 'ELLC', 'FASR', 'JDXQ', 'MAHD', 'TWWL', 'WHSK', 'EFAL', 'RYJG', 'MWCJ', 'MRYV', 'PILE', 'WTTE', 'ATKF', 'OTDW', 'PPCW', 'GOHE', 'HPRN', 'GGEJ', 'TLDV', 'LSFT', 'LFIE', 'GPML', 'KNIG', 'ADXF', 'MKMG', 'MXLH', 'GSXP', 'BLHT', 'PTID', 'FLCB', 'ADDP', 'DHXN', 'GBKV', 'RRBW', 'CUOT', 'KYRT', 'PCAK', 'CWTP', 'BMXQ', 'DYKI', 'AMPF', 'PRMI', 'CURA', 'LMCJ', 'LRGR', 'BGIJ', 'FNNK', "'/'", 'USSN', 'OSHB', 'JTFJ', 'SWHH', 'TMOD', 'OFOP', 'DGNN', 'FATR', 'GPON', 'MAEU', 'FRQT', 'GSDY', 'VENT', 'TKPS', 'XPOK', 'FMAE', 'OERT', 'WDWI', 'DNSL', 'VPEC', 'TIYI', 'ETSE', 'CJXE', 'FTJO', 'MCLQ', 'GJGQ', 'PCFA', 'CPNH', 'ROJD', 'THSL', 'SBYB', 'FHRC', 'BULK', 'EVFQ', 'VUTP', 'PISN', 'RKGC', 'LBTI', 'DLMT', 'COCA', 'RCTQ', 'LVES', 'IMPC', 'EFTT', 'ZHTP', 'FCKI', 'SELK', 'ECRR', 'SNLP', 'GCTN', 'JCDP', 'HDDR', 'TFCH', 'WTIK', 'PCFE', 'NWDW', 'PAFA', 'GATI'],
    "wbtc": ['IDLR', 'CMLF', 'JCTK', 'PARB', 'TSON', 'ADXH', 'SGAT', 'MHBQ', 'KTEV', 'PSED', 'JDLC', 'MXDP', 'AQEG', 'HKTH', 'EGHC', 'DEUC', 'ULSB', 'USON', 'CVDG', 'RLUP', 'WLGO', 'TRUO', 'TCED', 'OVFR', 'CGLQ', 'ELLC', 'ODYL', 'UNIC', 'ITIK', 'WHSK', 'PRQL', 'MWCJ', 'OTDW', 'GGEJ', 'LSFT', 'KNIG', 'ADXF', 'GSXP', 'BLHT', 'PTID', 'DULL', 'RRBW', 'GCIS', 'SONW', 'AMZN', 'PCAK', 'CWTP', 'NART', 'HDMU', 'PRMI', 'AMPF', 'CURA', 'GCNF', 'QXLC', 'USSN', 'OSHB', 'TMOD', 'OFOP', 'DGNN', 'GPON', 'FRQT', 'GSDY', 'VENT', 'XPOK', 'FDIH', 'OERT', 'WDWI', 'TIYI', 'ETSE', 'CJXE', 'PNDH', 'FTJO', 'CHRW', 'THSL', 'TILG', 'BULK', 'DLMT', 'COCA', 'MZSS', 'RCTQ', 'EFTT', 'ZHTP', 'FCKI', 'SELK', 'ECRR', 'TMYK', 'GCTN', 'WTIK', 'NWDW', 'GATI']
}
    
def get_credentials(terminal):
    url = f"{config['CORE_API_URL']}/appointments/parser/{terminal}/authentications"
    credentials = {}
    pool = set(SCAC_PER_TERMINAL[terminal])
    # subset = random.sample(pool, 5)
    subset = pool
    # subset = ["ADXH"]
    print(f"Fetching the credentials for {len(subset)} SCACs")
    for scac in tqdm.tqdm(subset):
        response = requests.post(
            url,
            data={"method": "scac", "terminal_name": "tti", "scac": scac},
            headers={
                "EA-Api-Key": config["LAMBDA_API_KEY"]
            }
        )
        # if response.status_code == 200:
        if response.status_code == 200:
            credentials[scac] = json.loads(response.text)
    return credentials

def get_consignees(scac, credential):
    credential = next(iter(credential.values()))
    data = {
        "srchTpCd": 123,
        "trkrCd": scac,
        "maxDispCnt": 2000,
        "outGateLastDays": 20000,
        "mtyTpCd": 1,
        "oprCd": "",
        "cntrSscoCd": "",
        "pTrkrCd": scac
    }
    proxies = {
        "http": credential.get("metadata", {}).get("proxy"),
        "https": credential.get("metadata", {}).get("proxy")
    }
    headers = {
        **HEADERS,
        "Cookie": credential.get("headers", {}).get("Cookie")
    }
    try:
        response = requests.post(
            "https://www.ttilgb.com/uiAap05Action/searchEmptyReturnContainerList.do",
            data=data,
            proxies=proxies,
            headers=headers,
            verify=False
        )
        data = response.json().get("resultObj", [])
        consignees = [
            row.get("cneeNm", "")
            for row in data
        ]
        return consignees
    except Exception as e:
        print(f"Request failed for {scac} ({str(e)})")
        print("Credential", json.dumps(credential, indent=4))
        print("Request params", json.dumps(data, indent=4), json.dumps(proxies, indent=4), json.dumps(headers, indent=4))
        raise Exception(e)
        # print(response.status_code, response.text)
        
if __name__ == "__main__":
    credentials = get_credentials("tti")
    # print(json.dumps(credentials, indent=4))
    data = []
    succeeded = []
    failed = []
    for scac, credential in tqdm.tqdm(credentials.items()):
        # consignees.extend(get_consignees(scac, credential))
        try:
            consignees = set([x for x in get_consignees(scac, credential) if x != ""])
            print(f"{scac} has {len(consignees)} unique consignees")
            for consignee in consignees:
                if consignee:
                    data.append([scac, consignee])
            succeeded.append(scac)
            time.sleep(5)
        except Exception as e:
            failed.append(scac)
            pass
    df = pd.DataFrame(data=data, columns=["SCAC", "Consignee"])
    df.to_csv("tti.csv")
    print(f"Total: {len(credentials)}\tSucceeded: {len(succeeded)}\tFailed: {len(failed)}")