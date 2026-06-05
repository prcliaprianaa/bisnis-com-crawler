"""
core/scraper.py
===============
Modul inti untuk mengambil dan mem-parse artikel dari bisnis.com.
Digunakan oleh kedua entrypoint (backtrack.py dan standard.py).
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# Config
REQUEST_DELAY = 1       # Delay antar request (detik), biar tidak diblokir
MAX_RETRIES = 3         # Maksimal percobaan ulang jika request gagal
RETRY_DELAY = 2         # Jeda antar retry (detik)


def fetch_page(url):
    """
    Mengambil konten HTML dari sebuah URL.
    - Delay antar request agar tidak membebani server
    - Retry otomatis jika gagal (maksimal 3x)
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            time.sleep(REQUEST_DELAY)
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Percobaan {attempt}/{MAX_RETRIES} gagal untuk {url}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Gagal mengambil {url} setelah {MAX_RETRIES} percobaan.")
                raise


def parse_article(url):
    """
    Parse satu halaman artikel bisnis.com dan ekstrak datanya.
    Return dict berisi: link, judul, isi, tanggal_terbit
    """
    html = fetch_page(url)
    soup = BeautifulSoup(html, 'html.parser')

    # 1. JUDUL
    title_tag = soup.find('meta', property='og:title')
    judul = title_tag['content'] if title_tag else ''

    if not judul:
        h1 = soup.find('h1')
        judul = h1.get_text(strip=True) if h1 else 'Tidak ada judul'

    # 2. TANGGAL TERBIT (sudah ISO 8601)
    date_tag = soup.find('meta', property='article:published_time')
    tanggal = date_tag['content'] if date_tag else ''

    # 3. ISI ARTIKEL
    isi = _extract_content(soup)

    return {
        'link': url,
        'judul': judul,
        'isi': isi,
        'tanggal_terbit': tanggal
    }


def _extract_content(soup):
    """
    Ekstrak isi artikel dari HTML bisnis.com.
    """
    selectors = [
        ('article', {'class': re.compile(r'detailsContent', re.I)}),
        ('div', {'class': re.compile(r'detailsContent', re.I)}),
        ('article', {}),
    ]

    content_div = None
    for tag, attrs in selectors:
        content_div = soup.find(tag, attrs)
        if content_div:
            break

    if not content_div:
        content_div = soup.find('body')

    if not content_div:
        return ''

    paragraphs = content_div.find_all('p')

    skip_keywords = [
        'baca juga', 'simak juga', 'disclaimer', 'google news',
        'cek berita', 'wa channel', 'langganan bisnis'
    ]

    isi_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) < 20:
            continue
        if any(kw in text.lower() for kw in skip_keywords):
            continue
        isi_parts.append(text)

    return '\n\n'.join(isi_parts)


def extract_date_from_url(url):
    """
    Ekstrak tanggal dari URL artikel bisnis.com.
    URL pattern: /read/YYYYMMDD/...
    """
    match = re.search(r'/read/(\d{8})/', url)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y%m%d').date()
    return None


def save_to_json(articles, filename):
    """
    Simpan list artikel ke file JSON di folder output/.
    """
    os.makedirs('output', exist_ok=True)
    filepath = os.path.join('output', filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

    logger.info(f"Berhasil menyimpan {len(articles)} artikel ke {filepath}")
    return filepath