"""
core/crawler.py
===============
Modul untuk meng-crawl halaman indeks bisnis.com
dan mengumpulkan link-link artikel.
"""

import logging
from bs4 import BeautifulSoup
from core.scraper import fetch_page, extract_date_from_url

logger = logging.getLogger(__name__)

INDEX_URL = 'https://www.bisnis.com/index'


def get_article_links(page=1):
    """
    Ambil semua link artikel dari satu halaman indeks bisnis.com.
    """
    url = f'{INDEX_URL}?page={page}'
    html = fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '/read/' in href and 'bisnis.com' in href:
            clean_url = href.split('?')[0].split('#')[0]
            if clean_url not in links:
                links.append(clean_url)

    return links


def get_links_by_date_range(start_date, end_date, max_pages=50):
    """
    Crawl halaman indeks dan kumpulkan link artikel
    dalam rentang start_date sampai end_date.
    """
    filtered_links = []

    for page in range(1, max_pages + 1):
        logger.info(f"Crawling halaman indeks {page}...")

        try:
            links = get_article_links(page)
        except Exception as e:
            logger.error(f"Gagal crawl halaman {page}: {e}")
            break

        if not links:
            logger.warning("Tidak ada link ditemukan, berhenti.")
            break

        oldest_on_page = None

        for link in links:
            article_date = extract_date_from_url(link)
            if article_date is None:
                continue

            if oldest_on_page is None or article_date < oldest_on_page:
                oldest_on_page = article_date

            if start_date <= article_date <= end_date:
                if link not in filtered_links:
                    filtered_links.append(link)

        if oldest_on_page and oldest_on_page < start_date:
            logger.info(f"Artikel sudah melewati {start_date}, berhenti crawling.")
            break

    logger.info(f"Ditemukan {len(filtered_links)} link artikel "
                f"dalam rentang {start_date} s/d {end_date}")
    return filtered_links


def get_latest_links(max_pages=2):
    """
    Ambil link artikel terbaru dari halaman indeks.
    """
    all_links = []

    for page in range(1, max_pages + 1):
        try:
            links = get_article_links(page)
            for link in links:
                if link not in all_links:
                    all_links.append(link)
        except Exception as e:
            logger.error(f"Gagal crawl halaman {page}: {e}")

    return all_links