from bs4 import BeautifulSoup
import requests

DIET_TAG_MAP = {
    'GF.gif': 'gluten_friendly',
    'HF.gif': 'halal_friendly',
    'V.gif': 'vegan',
    'M.gif': 'meatless',
    'P.gif': 'contains_pork',
}

def parse_menu_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    current_station = None

    # Find the menu container
    menu_col = soup.find('div', class_='col-8')
    if not menu_col:
        return items

    for element in menu_col.children:
        # Skip plain strings (whitespace/newlines)
        if not hasattr(element, 'name') or element.name is None:
            continue

        # Station header
        if element.name == 'h2' and 'category-header' in element.get('class', []):
            current_station = element.get_text(strip=True)

        # Menu item
        elif element.name == 'div' and 'menu-items' in element.get('class', []):
            link = element.find('a', href=True)
            if not link:
                continue

            name = link.get_text(strip=True)
            href = link['href']

            # Extract mid from href
            mid = None
            if 'mid=' in href:
                mid = href.split('mid=')[-1]

            # Extract diet tags from img alt attributes
            diet_tags = []
            for img in element.find_all('img'):
                src = img.get('src', '')
                filename = src.split('/')[-1]
                tag = DIET_TAG_MAP.get(filename)
                if tag:
                    diet_tags.append(tag)

            items.append({
                'name': name,
                'mid': mid,
                'nutrition_url': href,
                'station': current_station,
                'diet_tags': diet_tags,
            })

    return items


if __name__ == '__main__':
    session = requests.Session()
    menu_url = 'https://www.absecom.psu.edu/menus/user-pages/daily-menu.cfm'

    payload = {
        'selMenuDate': '6/30/26',
        'selMeal': 'Lunch',
        'selCampus': '11'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept-Encoding': 'identity',
    }

    r = session.post(menu_url, data=payload, headers=headers)
    items = parse_menu_page(r.text)

    print(f"Total items found: {len(items)}")
    for item in items:
        print(f"[{item['station']}] {item['name']} (mid={item['mid']}) tags={item['diet_tags']}")