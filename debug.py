from core.scraper import fetch_page
from bs4 import BeautifulSoup

url = "https://market.bisnis.com/read/20260604/7/1978377/ihsg-sudah-jatuh-33-tertimpa-rupiah-tembus-rp18000-per-dolar-as"

html = fetch_page(url)
soup = BeautifulSoup(html, 'html.parser')

# Cari semua <p> yang isinya panjang (kemungkinan konten artikel)
print("=== SEMUA PARAGRAF PANJANG ===")
for i, p in enumerate(soup.find_all('p')):
    text = p.get_text(strip=True)
    if len(text) > 50:
        parent = p.parent
        parent_class = parent.get('class', ['no-class'])
        parent_tag = parent.name
        print(f"[{i}] Parent: <{parent_tag} class='{parent_class}'>")
        print(f"    Text: {text[:100]}...")
        print()