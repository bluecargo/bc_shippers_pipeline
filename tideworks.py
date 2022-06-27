import requests
import pandas as pd
import tqdm
from bs4 import BeautifulSoup
from typing import Tuple, List
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
from dotenv import dotenv_values

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}

COMPANY_TYPES = [
    "CO_CONSIGNEE",
    "CO_BROKER_FORWARDING",
    "CO_SHIPPER"
]

CONFIG = dotenv_values(".env")

SEARCH_URL = "https://stl.tideworks.com/fc-STL/register/default.do?method=loadCompanies&emptyFirst=true&companyType"
COMPANY_CONTACT_INFO_URL = "https://stl.tideworks.com/fc-STL/register/default.do"
WEB_KEY = "6LctPAwUAAAAAGp-ikh2qNKAlCMadAZJR1zDXuFU"

def get_company_ids(company_type: str) -> List[Tuple[str, str, str]]:
    url = f"{SEARCH_URL}={company_type}"
    response = requests.get(url)
    html = BeautifulSoup(response.text, "html.parser")
    companies = html.find_all("option")
    return [
        (company.text, company.attrs.get("value"), company_type)
        for company in companies
        if company.text
    ]


def solve_captcha(website_key: str, website_url: str) -> str:
    solver = recaptchaV2Proxyless()
    solver.set_verbose(0)
    solver.set_key(CONFIG["CAPTCHA_KEY"])
    solver.set_website_url(website_url)
    solver.set_website_key(website_key)
    g_response = solver.solve_and_return_solution()
    if g_response != 0:
        return g_response
    else:
        raise Exception("Couldn't solve captcha")


def get_contact_info(session, company_id: str, company_type: str, captcha_response: str) -> Tuple[str, str, str]:
    data = {
        "companyName": "",
        "companyType": company_type,
        "truckerId": "",
        "companyId": company_id,
        "g-recaptcha-response": captcha_response
    }
    post_response = session.post(
        f"{COMPANY_CONTACT_INFO_URL}?method=checkCompanySelected",
        data=data,
        headers=HEADERS
    )
    mail_info_html = BeautifulSoup(post_response.text, "html.parser")
    sub_html = mail_info_html.find_all("div", {"class": "south_20"})[-1]
    contact_name = sub_html.find("h3", {"class": "north_20"}).text.strip()
    contact_phone = sub_html.text.strip()
    contact_email = sub_html.find_all("a")[0].text.strip()
    return contact_name, contact_phone, contact_email

if __name__ == "__main__":
    pre_data = []
    data = []
    print("Collecting company IDs ...")
    for company_type in tqdm.tqdm(COMPANY_TYPES):
        pre_data.extend(get_company_ids(company_type))
    session = requests.Session()
    print("Solving default captcha ...")
    g_response = solve_captcha(WEB_KEY, COMPANY_CONTACT_INFO_URL)
    if not g_response:
        raise Exception("Couldn't solve reCAPTCHA")
    print("Collecting company contact information ...")
    success = 0
    fail = 0
    sample = pre_data
    for record in tqdm.tqdm(sample):
        company_name, company_id, company_type = record
        try:
            contact_name, contact_phone, contact_email = get_contact_info(session, company_id, company_type, g_response)
        except:
            print(f"Couldn't find contact details for {company_name}")
            contact_name = ""
            contact_phone = ""
            contact_email = ""
        data.append([company_name, company_id, company_type, contact_name, contact_phone, contact_email])
    df = pd.DataFrame(data=data, columns=["company_name", "company_id", "company_type", "contact_name", "contact_phone", "contact_email"])
    df.to_csv("tideworks.csv")