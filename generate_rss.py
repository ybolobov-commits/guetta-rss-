import requests
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    response = requests.get(SHOW_URL, headers=headers, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все ссылки на миксы
    links = soup.find_all('a')
    mix_links = []
    
    for a in links:
        href = a.get('href', '')
        if '/mixes/' in href or '/tracks/' in href:
            full_url = BASE_URL + href if href.startswith('/') else href
            title = a.get_text(strip=True)
            if full_url not in [m['url'] for m in mix_links] and len(title) > 3:
                mix_links.append({'url': full_url, 'title': title})

    # Собираем первые 10 миксов
    for mix in mix_links[:10]:
        try:
            mix_resp = requests.get(mix['url'], headers=headers, timeout=10)
            mix_soup = BeautifulSoup(mix_resp.text, 'html.parser')
            
            # Ищем аудиофайл или плеер
            audio_tag = mix_soup.find('audio')
            audio_url = None
            if audio_tag:
                audio_url = audio_tag.get('src') or (audio_tag.find('source').get('src') if audio_tag.find('source') else None)

            fe = fg.add_entry()
            fe.id(mix['url'])
            fe.title(mix['title'])
            fe.link(href=mix['url'])
            fe.description(f'Mix: {mix["title"]}')

            # Если нашли прямой аудиофайл, добавляем его как энкложер подкаста
            if audio_url:
                if not audio_url.startswith('http'):
                    audio_url = BASE_URL + audio_url
                fe.enclosure(audio_url, 0, 'audio/mpeg')
        except Exception as inner_e:
            print(f"Error parsing mix page {mix['url']}: {inner_e}")
            continue

except Exception as e:
    print(f"Error fetching show page: {e}")

fg.rss_file('feed.xml')
