import cloudscraper
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

SHOW_URL = "https://globaldjmix.com/artists/david-guetta"
BASE_URL = "https://globaldjmix.com"

fg = FeedGenerator()
fg.id(SHOW_URL)
fg.title('David Guetta - GlobalDJMix')
fg.link(href=SHOW_URL, rel='alternate')
fg.description('David Guetta Podcast Feed')
fg.language('en')

# Обход защиты Cloudflare
scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})

try:
    response = scraper.get(SHOW_URL, timeout=20)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем карточки миксов
    items = soup.find_all('a', href=True)
    seen = set()

    for a in items:
        href = a['href']
        title = a.get_text(strip=True)

        if ('/mix/' in href or '/mixes/' in href) and href not in seen and len(title) > 3:
            seen.add(href)
            full_url = BASE_URL + href if href.startswith('/') else href

            fe = fg.add_entry()
            fe.id(full_url)
            fe.title(title)
            fe.link(href=full_url)
            fe.description(f'Mix: {title}')
            # Фейковый энкложер, чтобы AntennaPod видел пункт как аудио-выпуск
            fe.enclosure(full_url, 0, 'audio/mpeg')

            if len(seen) >= 20:
                break

except Exception as e:
    print(f"Error scraping: {e}")

fg.rss_file('feed.xml')
