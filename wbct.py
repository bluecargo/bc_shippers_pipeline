import requests
from dotenv import dotenv_values
import json
from bs4 import BeautifulSoup
import tqdm
import pandas as pd
import random
from html.parser import HTMLParser

config = dotenv_values(".env")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*"
}

SCACS = ['IDLR', 'CMLF', 'JCTK', 'PARB', 'TSON', 'ADXH', 'SGAT', 'MHBQ', 'KTEV', 'PSED', 'JDLC', 'MXDP', 'AQEG', 'HKTH', 'EGHC', 'DEUC', 'ULSB', 'USON', 'CVDG', 'RLUP', 'WLGO', 'TRUO', 'TCED', 'OVFR', 'CGLQ', 'ELLC', 'ODYL', 'UNIC', 'ITIK', 'WHSK', 'PRQL', 'MWCJ', 'OTDW', 'GGEJ', 'LSFT', 'KNIG', 'ADXF', 'GSXP', 'BLHT', 'PTID', 'DULL', 'RRBW', 'GCIS', 'SONW', 'AMZN', 'PCAK', 'CWTP', 'NART', 'HDMU', 'PRMI', 'AMPF', 'CURA', 'GCNF', 'QXLC', 'USSN', 'OSHB', 'TMOD', 'OFOP', 'DGNN', 'GPON', 'FRQT', 'GSDY', 'VENT', 'XPOK', 'FDIH', 'OERT', 'WDWI', 'TIYI', 'ETSE', 'CJXE', 'PNDH', 'FTJO', 'CHRW', 'THSL', 'TILG', 'BULK', 'DLMT', 'COCA', 'MZSS', 'RCTQ', 'EFTT', 'ZHTP', 'FCKI', 'SELK', 'ECRR', 'TMYK', 'GCTN', 'WTIK', 'NWDW', 'GATI']

def get_credential(scac):
    url = f"{config['CORE_API_URL']}/appointments/parser/wbct/authentications"
    response = requests.post(
        url,
        data={"method": "scac", "terminal_name": "wbct", "scac": scac},
        headers={
            "EA-Api-Key": config["LAMBDA_API_KEY"]
        }
    )
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Couldn't get credentials for {scac} ({response.status_code})")

def get_consignees(scac, credentials):
    credential = next(iter(credentials.values()))
    data = {
        "InquiryType": "ByCategory",
        "TruckerCode": scac,
        "SortKey": "ApptDateTime",
        # "ShowAllImportContainersStillOut": {
        #     0: "true",
        #     1: "false"
        # },
        "ShowAllImportContainersStillOut": "true",
        "CntrSscoCode": "",
        "LastExitGateDays": "2000",
        # "ShowAllActivePendingAppts": {
        #     0: "true",
        #     1: "false"
        # },
        "ShowAllActivePendingAppts": "false",
        # "ApptSscoCode": "",
        "ContainerNumber": "",
        "SkipCheckDigitRecalculation": "false"
    }
    proxies = {
        "http": credential.get("metadata", {}).get("proxy"),
        "https": credential.get("metadata", {}).get("proxy")
    }
    headers = {
        **HEADERS,
        "Cookie": credential.get("headers", {}).get("Cookie")
    }
    response = requests.post(
        "https://voyagertrack.portsamerica.com/Report/EmptyIn/SearchEmptyIns?pageSize=2000",
        data=data,
        proxies=proxies,
        headers=headers,
        verify=False
    )
    html = BeautifulSoup(response.text, "html.parser")
    # tab = html.find("table", {"class": "appointment collapsible"})
    tab = html.find("table", {"class": "appointment collapsible"})
    rows = tab.find_all("tbody")[0].find_all("tr", {"data-move-type": "EmptyIn"})
    consignees = [
        row.find_all("td")[8].text.strip()
        for row in rows
    ]
    return set([x for x in consignees if x != ""])

if __name__ == "__main__":
    data = []
    results = {}
    # pool = random.sample(SCACS, 5)
    for scac in tqdm.tqdm(SCACS):
        try:
            cred = get_credential(scac)
            consignees = get_consignees(scac, cred)
            for consignee in consignees:
                data.append([scac, consignee])
            results[scac] = True
        except:
            results[scac] = False
    print(f"Total: {len(results)}\tFailed: {len([x for x in results if not x])}\tSuccess: {len([x for x in results if x])}")
    df = pd.DataFrame(data=data, columns=["SCAC", "consignee"])
    df.to_csv("wbct.csv")



    # print(config)

    # print("\n")
    # print(cred)
    # print(json.dumps(cred["adpexpress"].get("headers").get("Cookie"), indent=4)[1:-1])
