import requests
from feedgen.feed import FeedGenerator

# URL API для получения списка миксов David Guetta
API_URL = "https://globaldjmix.com/api/mixes?artist=david-guetta&limit=20"
BASE_URL = "https://globaldjmix.com"

fg = FeedGenerator()
fg.id("https://globaldjmix.com/artists/david-guetta")
fg.title('David Guetta - GlobalDJMix')
fg.link(href="https://globaldjmix.com/artists/david-guetta", rel='alternate')
fg.description('David Guetta Mixes and Podcasts')
fg.language('en')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

try:
    response = requests.get(API_URL, headers=headers, timeout=15)
    
    # Если API вернуло JSON с данными
    if response.status_code == 200 and 'json' in response.headers.get('Content-Type', ''):
        data = response.json()
        mixes = data.get('mixes', data.get('items', data if isinstance(data, list) else []))
        
        for mix in mixes:
            title = mix.get('title') or mix.get('name') or 'David Guetta Mix'
            slug = mix.get('slug') or mix.get('id')
            mix_url = f"{BASE_URL}/mix/{slug}" if slug else fg.id()
            audio_url = mix.get('audio_url') or mix.get('file') or mix.get('stream_url')

            fe = fg.add_entry()
            fe.id(mix_url)
            fe.title(title)
            fe.link(href=mix_url)
            fe.description(f'Tracklist & Stream: {title}')

            if audio_url:
                if not audio_url.startswith('http'):
                    audio_url = BASE_URL + audio_url
                fe.enclosure(audio_url, 0, 'audio/mpeg')
    else:
        # Резервный вариант: парсинг прямых потоковых ссылок с HTML
        html_resp = requests.get("https://globaldjmix.com/artists/david-guetta", headers=headers, timeout=15)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_resp.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            if '/mix/' in a['href'] or '/mixes/' in a['href']:
                title = a.get_text(strip=True)
                if len(title) > 5:
                    link = BASE_URL + a['href'] if a['href'].startswith('/') else a['href']
                    fe = fg.add_entry()
                    fe.id(link)
                    fe.title(title)
                    fe.link(href=link)
                    fe.description(f'Mix: {title}')
                    # Заглушка аудио-потока для корректного распознавания AntennaPod
                    fe.enclosure(link, 0, 'audio/mpeg')

except Exception as e:
    print(f"Error: {e}")

fg.rss_file('feed.xml')
