"""Throwaway test: does a cloud machine get the same answers from public data sites as a home connection?

One request per site, no keys sent. Run it in both places and compare the two outputs.
"""

import csv
import subprocess
import sys
import tempfile
import time

USER_AGENT = "reach-test/1.0 (one request per site; public data research)"
TIMEOUT_SECONDS = "30"
PAUSE_SECONDS = 1.2
BLOCK_SIGNS = (
    "access denied", "request unsuccessful", "just a moment", "attention required",
    "captcha", "incapsula", "you don't have permission", "request blocked", "forbidden",
)

TARGETS = [
    ("census-api", "https://api.census.gov/data/timeseries/bds?get=FIRMDEATH_FIRMS&for=us:*&NAICS=423&YEAR=2022"),
    ("census-files", "https://www2.census.gov/programs-surveys/cbp/datasets/"),
    ("census-site", "https://www.census.gov/econ/currentdata/"),
    ("bls-api", "https://api.bls.gov/publicAPI/v2/timeseries/data/CES0000000001"),
    ("bls-files", "https://download.bls.gov/pub/time.series/ce/ce.series"),
    ("bls-site", "https://www.bls.gov/iif/"),
    ("dol-api", "https://apiprod.dol.gov/v4/get/MSHA/accident/json?limit=1"),
    ("dol-unemployment", "https://oui.doleta.gov/unemploy/claims.asp"),
    ("osha-site", "https://www.osha.gov/"),
    ("sba-data", "https://data.sba.gov/api/3/action/package_search?q=7a&rows=1"),
    ("irs-files", "https://www.irs.gov/pub/irs-soi/eo4.csv"),
    ("irs-site", "https://www.irs.gov/statistics"),
    ("sec-files", "https://www.sec.gov/files/company_tickers.json"),
    ("sec-search", "https://efts.sec.gov/LATEST/search-index?q=%22supply%20chain%22&forms=10-K"),
    ("epa-data", "https://data.epa.gov/efservice/tri_facility/state_abbr/VT/rows/0:1/JSON"),
    ("epa-echo", "https://echo.epa.gov/"),
    ("usaspending", "https://api.usaspending.gov/api/v2/references/toptier_agencies/"),
    ("reginfo", "https://www.reginfo.gov/public/do/PRAMain"),
    ("regulations-api", "https://api.regulations.gov/v4/documents?page%5Bsize%5D=5"),
    ("federal-register", "https://www.federalregister.gov/api/v1/documents.json?per_page=1"),
    ("fda-api", "https://api.fda.gov/device/classification.json?limit=1"),
    ("clinical-trials", "https://clinicaltrials.gov/api/v2/studies?pageSize=1"),
    ("nhtsa-api", "https://api.nhtsa.gov/recalls/recallsByVehicle?make=honda&model=accord&modelYear=2019"),
    ("fema-api", "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries?$top=1"),
    ("uscis-site", "https://www.uscis.gov/tools/reports-and-studies/immigration-and-citizenship-data"),
    ("cfpb-complaints", "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?size=1"),
    ("hmda-api", "https://ffiec.cfpb.gov/v2/data-browser-api/view/nationwide/aggregations?years=2023&actions_taken=3"),
    ("courtlistener", "https://www.courtlistener.com/api/rest/v4/search/?q=antitrust&type=o&page_size=1"),
    ("eia-api", "https://api.eia.gov/v2/"),
    ("usda-quickstats", "https://quickstats.nass.usda.gov/api/get_counts/?commodity_desc=CORN"),
    ("hud-site", "https://www.huduser.gov/portal/datasets/fmr.html"),
    ("medicaid-data", "https://data.medicaid.gov/api/1/metastore/schemas/dataset/items?show-reference-ids=false"),
    ("openalex", "https://api.openalex.org/works?per-page=1"),
    ("arxiv", "https://export.arxiv.org/api/query?search_query=all:robotics&max_results=1"),
    ("onet", "https://www.onetcenter.org/database.html"),
    ("washington-state-data", "https://data.wa.gov/resource/7w96-mhxh.json?$limit=1"),
    ("new-york-city-data", "https://data.cityofnewyork.us/resource/erm2-nwe9.json?$limit=1"),
    ("socrata-catalogue", "https://api.us.socrata.com/api/catalog/v1?limit=1"),
    ("oversight-gov", "https://www.oversight.gov/reports"),
    ("ssa-site", "https://www.ssa.gov/open/data/"),
    ("nasa-tech-transfer", "https://technology.nasa.gov/api/api/patent/sensor"),
    ("tariff-schedule", "https://hts.usitc.gov/reststop/search?keyword=pump"),
    ("ftc-site", "https://www.ftc.gov/enforcement/refunds"),
    ("nlrb-site", "https://www.nlrb.gov/reports/graphs-data"),
    ("eeoc-site", "https://www.eeoc.gov/data"),
    ("us-courts", "https://www.uscourts.gov/statistics-reports"),
    ("hugging-face", "https://huggingface.co/api/models?sort=trendingScore&limit=1"),
    ("github-api", "https://api.github.com/search/repositories?q=topic:robotics&per_page=1"),
]


def fetch(url: str) -> tuple[str, int, str]:
    with tempfile.NamedTemporaryFile() as body:
        result = subprocess.run(
            ["curl", "-s", "-L", "-m", TIMEOUT_SECONDS, "-A", USER_AGENT, "-o", body.name,
             "-w", "%{http_code}", url],
            capture_output=True, text=True,
        )
        status = result.stdout.strip() or "000"
        data = open(body.name, "rb").read()
    if status == "000":
        return "no-answer", 0, f"curl exit {result.returncode}"
    text = data[:4096].decode("utf-8", errors="replace").lower()
    return status, len(data), next((sign for sign in BLOCK_SIGNS if sign in text), "")


def main() -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow(["name", "status", "bytes", "block_sign"])
    for name, url in TARGETS:
        writer.writerow([name, *fetch(url)])
        sys.stdout.flush()
        time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
