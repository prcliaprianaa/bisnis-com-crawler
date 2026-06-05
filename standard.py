"""
standard.py — Entrypoint 2: Mode Standard
==========================================
Cara pakai:
    python standard.py --interval 300
"""

import argparse
import time
import logging
from datetime import datetime
from core.crawler import get_latest_links
from core.scraper import parse_article, save_to_json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Bisnis.com Crawler - Mode Standard'
    )
    parser.add_argument('--interval', type=int, default=300, help='Interval dalam detik (default: 300)')
    parser.add_argument('--max-pages', type=int, default=2, help='Halaman indeks per cycle (default: 2)')

    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("BISNIS.COM CRAWLER - MODE STANDARD")
    logger.info(f"Interval: {args.interval} detik")
    logger.info("Tekan Ctrl+C untuk berhenti")
    logger.info("=" * 50)

    seen_links = set()

    try:
        while True:
            logger.info("Memulai crawling...")

            try:
                links = get_latest_links(max_pages=args.max_pages)
            except Exception as e:
                logger.error(f"Gagal crawl: {e}")
                logger.info(f"Menunggu {args.interval} detik...")
                time.sleep(args.interval)
                continue

            new_links = [link for link in links if link not in seen_links]

            if not new_links:
                logger.info("Tidak ada artikel baru.")
            else:
                logger.info(f"Ditemukan {len(new_links)} artikel baru!")

                articles = []
                for i, link in enumerate(new_links, 1):
                    logger.info(f"[{i}/{len(new_links)}] {link}")
                    try:
                        article = parse_article(link)
                        articles.append(article)
                        seen_links.add(link)
                    except Exception as e:
                        logger.error(f"Gagal scrape: {e}")

                if articles:
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"standard_{ts}.json"
                    save_to_json(articles, filename)

            logger.info(f"Menunggu {args.interval} detik...")
            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info(f"Crawler dihentikan. Total artikel: {len(seen_links)}")


if __name__ == '__main__':
    main()