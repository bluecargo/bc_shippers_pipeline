import requests
from dotenv import dotenv_values
import json
from html.parser import HTMLParser

config = dotenv_values(".env")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

SCAC_PER_TERMINAL = {
    "tti": ['CMLF', 'JCTK', 'PARB', 'KFKC', 'ADXH', 'SGAT', 'ROLY', 'TIKG', 'MHBQ', 'KTEV', 'PSED', 'TGSM', 'JDLC', 'YMLU', 'MXDP', 'AQEG', 'HKTH', 'BOLS', 'PACL', 'SNEA', 'OSGB', 'EGHC', 'DEUC', 'DWCH', 'AANA', 'USON', 'CFMM', 'NOTQ', 'NGLN', 'ISNC', 'RLUP', 'CCOO', 'CVDG', 'TRUO', 'WLGO', 'DPHE', 'CPTD', 'TCED', 'EOIA', 'RTIB', 'CGLQ', 'KCNT', 'ELLC', 'FASR', 'JDXQ', 'MAHD', 'TWWL', 'WHSK', 'EFAL', 'RYJG', 'MWCJ', 'MRYV', 'PILE', 'WTTE', 'ATKF', 'OTDW', 'PPCW', 'GOHE', 'HPRN', 'GGEJ', 'TLDV', 'LSFT', 'LFIE', 'GPML', 'KNIG', 'ADXF', 'MKMG', 'MXLH', 'GSXP', 'BLHT', 'PTID', 'FLCB', 'ADDP', 'DHXN', 'GBKV', 'RRBW', 'CUOT', 'KYRT', 'PCAK', 'CWTP', 'BMXQ', 'DYKI', 'AMPF', 'PRMI', 'CURA', 'LMCJ', 'LRGR', 'BGIJ', 'FNNK', "'/'", 'USSN', 'OSHB', 'JTFJ', 'SWHH', 'TMOD', 'OFOP', 'DGNN', 'FATR', 'GPON', 'MAEU', 'FRQT', 'GSDY', 'VENT', 'TKPS', 'XPOK', 'FMAE', 'OERT', 'WDWI', 'DNSL', 'VPEC', 'TIYI', 'ETSE', 'CJXE', 'FTJO', 'MCLQ', 'GJGQ', 'PCFA', 'CPNH', 'ROJD', 'THSL', 'SBYB', 'FHRC', 'BULK', 'EVFQ', 'VUTP', 'PISN', 'RKGC', 'LBTI', 'DLMT', 'COCA', 'RCTQ', 'LVES', 'IMPC', 'EFTT', 'ZHTP', 'FCKI', 'SELK', 'ECRR', 'SNLP', 'GCTN', 'JCDP', 'HDDR', 'TFCH', 'WTIK', 'PCFE', 'NWDW', 'PAFA', 'GATI'],
    "wbct": ['IDLR', 'CMLF', 'JCTK', 'PARB', 'TSON', 'ADXH', 'SGAT', 'MHBQ', 'KTEV', 'PSED', 'JDLC', 'MXDP', 'AQEG', 'HKTH', 'EGHC', 'DEUC', 'ULSB', 'USON', 'CVDG', 'RLUP', 'WLGO', 'TRUO', 'TCED', 'OVFR', 'CGLQ', 'ELLC', 'ODYL', 'UNIC', 'ITIK', 'WHSK', 'PRQL', 'MWCJ', 'OTDW', 'GGEJ', 'LSFT', 'KNIG', 'ADXF', 'GSXP', 'BLHT', 'PTID', 'DULL', 'RRBW', 'GCIS', 'SONW', 'AMZN', 'PCAK', 'CWTP', 'NART', 'HDMU', 'PRMI', 'AMPF', 'CURA', 'GCNF', 'QXLC', 'USSN', 'OSHB', 'TMOD', 'OFOP', 'DGNN', 'GPON', 'FRQT', 'GSDY', 'VENT', 'XPOK', 'FDIH', 'OERT', 'WDWI', 'TIYI', 'ETSE', 'CJXE', 'PNDH', 'FTJO', 'CHRW', 'THSL', 'TILG', 'BULK', 'DLMT', 'COCA', 'MZSS', 'RCTQ', 'EFTT', 'ZHTP', 'FCKI', 'SELK', 'ECRR', 'TMYK', 'GCTN', 'WTIK', 'NWDW', 'GATI']
}

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
        "CntrSscoCode": "",
        "LastExitGateDays": "21",
        # "ShowAllActivePendingAppts": {
        #     0: "true",
        #     1: "false"
        # },
        "ShowAllActivePendingAppts": "false",
        # "ApptSscoCode": "",
        "ContainerNumber": "",
        "SkipCheckDigitRecalculation": "False"
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
        "https://voyagertrack.portsamerica.com/SearchEmptyIns",
        data=data,
        proxies=proxies,
        headers=headers,
        verify=False
    )
    # response = requests.get(
    #     "https://voyagertrack.portsamerica.com/Report/EmptyIn/EmptyIn?_=1656002791739",
    #     data=data,
    #     proxies=proxies,
    #     headers=headers,
    #     verify=False
    # )
    print(response.text)

if __name__ == "__main__":
    cred = get_credential("ADXH")
    get_consignees("ADXH", cred)
