"""
backtrack.py — Entrypoint 1: Mode Backtrack
============================================
Cara pakai:
    python backtrack.py --start 2026-06-01 --end 2026-06-04
"""

import argparse
import logging
from datetime import datetime
from core.crawler import get_links_by_date_range
from core.scraper import parse_article, save_to_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Bisnis.com Crawler - Mode Backtrack'
    )
    parser.add_argument('--start', required=True, help='Tanggal mulai (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='Tanggal akhir (YYYY-MM-DD)')
    parser.add_argument('--max-pages', type=int, default=50, help='Max halaman indeks (default: 50)')

    args = parser.parse_args()

    start_date = datetime.strptime(args.start, '%Y-%m-%d').date()
    end_date = datetime.strptime(args.end, '%Y-%m-%d').date()

    if start_date > end_date:
        logger.error("Start date harus sebelum end date.")
        return

    logger.info("=" * 50)
    logger.info("BISNIS.COM CRAWLER - MODE BACKTRACK")
    logger.info(f"Rentang: {start_date} s/d {end_date}")
    logger.info("=" * 50)

    # Step 1: Kumpulkan link dalam rentang tanggal
    links = get_links_by_date_range(start_date, end_date, max_pages=args.max_pages)

    if not links:
        logger.warning("Tidak ada artikel ditemukan dalam rentang tersebut.")
        return

    # Step 2: Scrape setiap artikel
    logger.info(f"Memulai scraping {len(links)} artikel...")
    articles = []

    for i, link in enumerate(links, 1):
        logger.info(f"[{i}/{len(links)}] {link}")
        try:
            article = parse_article(link)
            articles.append(article)
        except Exception as e:
            logger.error(f"Gagal scrape: {e}")

    # Step 3: Simpan ke JSON
    if articles:
        filename = f"backtrack_{start_date}_{end_date}.json"
        save_to_json(articles, filename)
    else:
        logger.warning("Tidak ada artikel yang berhasil di-scrape.")


if __name__ == '__main__':
    main()