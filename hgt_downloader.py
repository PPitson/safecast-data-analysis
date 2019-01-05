import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import List

import requests
from bs4 import BeautifulSoup

FILES_DIR = "hgt_files"


def download_files() -> None:
    file_urls = get_file_urls()
    print(len(file_urls), "files to download")
    with ThreadPoolExecutor() as pool:
        for downloaded_url in pool.map(download_file, file_urls):
            print(downloaded_url)


def get_file_urls() -> List[str]:
    file_urls = []
    urls = [
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Africa/",
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Australia/",
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Eurasia/",
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Islands/",
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/North_America/",
        "https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/South_America/"
    ]
    for url in urls:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [url + link["href"] for link in soup.find_all("a") if "hgt.zip" in link["href"]]
        print(len(links), "files in", url)
        file_urls.extend(links)
    return file_urls


def download_file(url: str) -> str:
    resp = requests.get(url)
    with zipfile.ZipFile(BytesIO(resp.content)) as zip_ref:
        zip_ref.extractall(FILES_DIR)
    return url


if __name__ == '__main__':
    download_files()
