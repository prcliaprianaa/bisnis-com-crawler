# Bisnis.com Crawler & Scraper

Crawler dan scraper untuk mengambil artikel dari [bisnis.com](https://www.bisnis.com) dengan dua mode operasi: **Backtrack** dan **Standard**.

## Fitur

- **Mode Backtrack**: Mengambil artikel dalam rentang tanggal tertentu (start date - end date)
- **Mode Standard**: Berjalan terus-menerus (long-running), secara berkala mengambil artikel terbaru dengan interval yang dapat dikonfigurasi
- Output berupa file JSON berisi link, judul, isi artikel, dan tanggal terbit (format ISO 8601)

## Instalasi

```bash
# Clone repository
git clone https://github.com/prcliaprianaa/bisnis-crawler.git
cd bisnis-crawler

# Install dependencies
pip install -r requirements.txt
```

## Cara Penggunaan

### Mode Backtrack

Mengambil artikel berdasarkan rentang tanggal:

```bash
python backtrack.py --start 2026-06-01 --end 2026-06-04
```

Parameter:
| Parameter | Wajib | Keterangan |
|-----------|-------|------------|
| `--start` | Ya | Tanggal mulai (format: YYYY-MM-DD) |
| `--end` | Ya | Tanggal akhir (format: YYYY-MM-DD) |
| `--max-pages` | Tidak | Maksimal halaman indeks yang di-crawl (default: 50) |

Output: `output/backtrack_2026-06-01_2026-06-04.json`

### Mode Standard

Mengambil artikel terbaru secara berkala:

```bash
python standard.py --interval 300
```

Parameter:
| Parameter | Wajib | Keterangan |
|-----------|-------|------------|
| `--interval` | Tidak | Interval penarikan dalam detik (default: 300 = 5 menit) |
| `--max-pages` | Tidak | Jumlah halaman indeks per siklus (default: 2) |

Tekan `Ctrl+C` untuk menghentikan. Output: `output/standard_YYYYMMDD_HHMMSS.json`

## Format Output JSON

```json
[
  {
    "link": "https://market.bisnis.com/read/20260604/7/1978377/contoh-artikel",
    "judul": "Contoh Judul Artikel",
    "isi": "Isi lengkap artikel...",
    "tanggal_terbit": "2026-06-04T12:14:28+07:00"
  }
]
```

## Arsitektur

```
bisnis-crawler/
├── core/                  # Modul inti (dipakai kedua mode)
│   ├── __init__.py
│   ├── scraper.py         # Fungsi fetch & parse artikel
│   └── crawler.py         # Fungsi crawl halaman indeks
├── backtrack.py           # Entrypoint 1: mode Backtrack
├── standard.py            # Entrypoint 2: mode Standard
├── output/                # Folder output JSON
├── requirements.txt
└── README.md
```

### Penjelasan Modul

**`core/scraper.py`** — Modul dasar yang berisi fungsi-fungsi inti:
- `fetch_page(url)` — Mengambil konten HTML dari URL
- `parse_article(url)` — Mem-parse halaman artikel dan mengekstrak judul, isi, dan tanggal terbit
- `extract_date_from_url(url)` — Mengekstrak tanggal dari pola URL bisnis.com (`/read/YYYYMMDD/...`)
- `save_to_json(articles, filename)` — Menyimpan list artikel ke file JSON

**`core/crawler.py`** — Modul untuk menjelajahi halaman indeks:
- `get_article_links(page)` — Mengambil semua link artikel dari satu halaman indeks
- `get_links_by_date_range(start, end)` — Mengumpulkan link artikel dalam rentang tanggal (untuk mode Backtrack)
- `get_latest_links()` — Mengambil link artikel terbaru (untuk mode Standard)

**`backtrack.py`** dan **`standard.py`** adalah dua entrypoint terpisah yang masing-masing mengimpor dan menggunakan fungsi dari modul `core/` yang sama.

### Alur Kerja

```
                    ┌─────────────┐     ┌──────────────┐
                    │ backtrack.py │     │ standard.py  │
                    │ (date range)│     │ (long-running)│
                    └──────┬──────┘     └──────┬───────┘
                           │                    │
                           └────────┬───────────┘
                                    ▼
                    ┌───────────────────────────────┐
                    │        core/ (shared)          │
                    │  scraper.py  ←→  crawler.py    │
                    └───────────────┬───────────────┘
                                    │
                           ┌────────┴────────┐
                           ▼                  ▼
                    ┌────────────┐    ┌──────────────┐
                    │ bisnis.com │    │ output/*.json │
                    └────────────┘    └──────────────┘
```

## Teknologi

- **Python 3.8+**
- **Requests** — HTTP client untuk mengambil halaman web
- **BeautifulSoup4** — Parser HTML untuk mengekstrak data dari halaman web
