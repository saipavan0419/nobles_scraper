"""
Create CSV file with the required fields by parsing the JSON files using Pandas
"""
import sys
import logging
from typing import Any
import requests

import pandas as pd

LAUREATE_URL = "https://api.nobelprize.org/v1/laureate.json"
COUNTRY_URL = "https://api.nobelprize.org/v1/country.json"

def create_logger():
    """
    return logger object
    """
    logging.basicConfig(
        filename="parse_noble.log",
        format="%(asctime)s %(message)s",
        filemode="w")
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    return logger

def download_json(url: str, log_obj: Any):
    """
    return JSON response
    Download
    """
    try:
        resp = requests.get(url, timeout=5)
        json_resp = resp.json()
    except (requests.exceptions.JSONDecodeError) as err:
        log_obj.debug(f"Error {err} Occurred")
        raise sys.exit()
    else:
        return json_resp

def parse(log_obj: Any):
    """
    Parse laureate file and generate the CSV with required columns like
    id, name, born, unique_catg, unique_year, gender, country_name.
    Country_name will have to be looked up from country json file.
    """
    laureates_resp = download_json(LAUREATE_URL, log_obj)
    laureates_df = pd.DataFrame(laureates_resp.get("laureates", []))
    country_resp = download_json(COUNTRY_URL, log_obj)
    countries_map = {i.get("code"):i.get("name") for i in country_resp["countries"] if i}
    laureates_df['unique_category'] = laureates_df['prizes'].apply(
        lambda x: ";".join(i["category"] for i in x))
    laureates_df['unique_year'] = laureates_df['prizes'].apply(
        lambda x: ";".join(i["year"] for i in x))
    laureates_df["country_name"] = laureates_df["bornCountryCode"].apply(
        lambda x: countries_map.get(x))
    laureates_df["name"] = laureates_df["firstname"].fillna("") + " " + laureates_df["surname"].fillna("")
    req_cols = ["id", "name", "born", "unique_category", "unique_year", "gender", "country_name"]
    laureates_df.to_csv("nobles.csv", columns=req_cols, index=False)


if __name__ == "__main__":
    log_obj = create_logger()
    parse(log_obj)
