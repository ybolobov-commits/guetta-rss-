import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Ссылка на страницу с шоу
SHOW_URL = "https://globaldjmix.com/artists/david-guetta"
BASE_URL = "https://globaldjmix.com"

# Создаем структуру RSS-ленты
fg = FeedGenerator()
fg.id(SHOW_URL)
fg.title('David Guetta - GlobalDJMix')
fg.link(href=SHOW_URL, rel='alternate')
fg.description('Автоматический RSS-фид выпусков David Guetta')
fg.language('en')

# Загружаем страницу
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(SHOW_URL, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Ищем выпуски на странице
items = soup.select('.mix-item, .post-item, .article-item')

for item in items[:15]:
    title_elem = item.select_one('a')
    if not title_elem:
        continue

    title = title_elem.get_text(strip=True)
    link = title_elem.get('href', '')

    if not link.startswith('http'):
        link = BASE_URL + link

    if title and link:
        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.description(f'Выпуск: {title}')

# Сохраняем результат в файл feed.xml
fg.rss_file('feed.xml')
