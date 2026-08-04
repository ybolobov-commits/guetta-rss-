import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

SHOW_URL = "https://globaldjmix.com/artists/david-guetta"
BASE_URL = "https://globaldjmix.com"

fg = FeedGenerator()
fg.id(SHOW_URL)
fg.title('David Guetta - GlobalDJMix')
fg.link(href=SHOW_URL, rel='alternate')
fg.description('David Guetta Mixes & Podcasts')
fg.language('en')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

try:
    response = requests.get(SHOW_URL, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем все ссылки на миксы
    mix_elements = soup.select('a[href*="/mix/"], a[href*="/mixes/"]')
    
    seen = set()
    count = 0

    for a in mix_elements:
        href = a.get('href', '')
        title = a.get_text(strip=True)
        
        if href and title and len(title) > 3 and href not in seen:
            seen.add(href)
            full_url = BASE_URL + href if href.startswith('/') else href

            fe = fg.add_entry()
            fe.id(full_url)
            fe.title(title)
            fe.link(href=full_url)
            fe.description(f'Listen to {title} on GlobalDJMix')
            
            count += 1
            if count >= 20:
                break

except Exception as e:
    print(f"Error: {e}")

fg.rss_file('feed.xml')
