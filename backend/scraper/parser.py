from bs4 import BeautifulSoup
import re

def parse_value(text):
    """Extract numeric value from a string like '13.9g' or '479.2mg'"""
    if not text or text.strip() == '-':
        return None
    match = re.search(r'[\d.]+', text.strip())
    return float(match.group()) if match else None

def get_nutrient_value(soup, label):
    """Find a <b> tag with matching label and return the sibling text after it"""
    for b_tag in soup.find_all('b'):
        if b_tag.get_text(strip=True).rstrip(':') == label:
            # The value is the next sibling text node
            next_sibling = b_tag.next_sibling
            if next_sibling:
                return str(next_sibling).strip()
    return None

def parse_nutrition_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # DEBUG - remove after fixing
    for b in soup.find_all('b'):
        print(repr(b.get_text(strip=True)), repr(b.next_sibling))
    # Item name — h1 with class rpt-ml-20
    name_tag = soup.find('h1', class_='rpt-ml-20')
    name = name_tag.get_text(strip=True) if name_tag else None

    # Serving size and calories — inside <th> as <b>Label:</b> value
    serving_size = get_nutrient_value(soup, 'Serving Size')
    calories = parse_value(get_nutrient_value(soup, 'Calories'))
    calories_from_fat = parse_value(get_nutrient_value(soup, 'Calories from Fat'))

    # Macros from table cells
    total_fat = parse_value(get_nutrient_value(soup, 'Total Fat'))
    sat_fat = parse_value(get_nutrient_value(soup, 'Sat Fat'))
    trans_fat = parse_value(get_nutrient_value(soup, 'Trans Fat'))
    cholesterol = parse_value(get_nutrient_value(soup, 'Cholesterol'))
    sodium = parse_value(get_nutrient_value(soup, 'Sodium'))
    total_carb = parse_value(get_nutrient_value(soup, 'Total Carb'))
    fiber = parse_value(get_nutrient_value(soup, 'Dietary Fiber'))
    sugars = parse_value(get_nutrient_value(soup, 'Sugars'))
    added_sugar = parse_value(get_nutrient_value(soup, 'Added Sugar'))
    protein = parse_value(get_nutrient_value(soup, 'Protein'))
    vitamin_d = parse_value(get_nutrient_value(soup, 'Vitamin D'))
    calcium = parse_value(get_nutrient_value(soup, 'Calcium'))
    iron = parse_value(get_nutrient_value(soup, 'Iron'))
    potassium = parse_value(get_nutrient_value(soup, 'Potassium'))

    # Ingredients and allergens
    ingredients = None
    allergens = None
    for b_tag in soup.find_all('b'):
        if b_tag.get_text(strip=True) == 'Ingredients:':
            ingredients = b_tag.next_sibling
            ingredients = str(ingredients).strip() if ingredients else None
        if b_tag.get_text(strip=True) == 'Allergens:':
            allergens = b_tag.next_sibling
            allergens = str(allergens).strip() if allergens else None

    return {
        'name': name,
        'serving_size': serving_size,
        'calories': calories,
        'calories_from_fat': calories_from_fat,
        'total_fat_g': total_fat,
        'sat_fat_g': sat_fat,
        'trans_fat_g': trans_fat,
        'cholesterol_mg': cholesterol,
        'sodium_mg': sodium,
        'total_carb_g': total_carb,
        'fiber_g': fiber,
        'sugars_g': sugars,
        'added_sugar_g': added_sugar,
        'protein_g': protein,
        'vitamin_d_mcg': vitamin_d,
        'calcium_mg': calcium,
        'iron_mg': iron,
        'potassium_mg': potassium,
        'ingredients': ingredients,
        'allergens': allergens,
    }

if __name__ == '__main__':
    import requests
    
    session = requests.Session()
    
    menu_url = "https://www.absecom.psu.edu/menus/user-pages/daily-menu.cfm"
    
    payload = {
        'selMenuDate': '6/30/26',
        'selMeal': 'Lunch',
        'selCampus': '11'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept-Encoding': 'identity',
        'Referer': menu_url,
    }
    
    # Step 1: Get today's menu
    menu_response = session.post(menu_url, data=payload, headers=headers)
    soup_menu = BeautifulSoup(menu_response.text, 'html.parser')
    links = soup_menu.find_all('a', href=True)
    nutrition_links = [l['href'] for l in links if 'nutrition-label' in l['href']]
    
    print(f"Found {len(nutrition_links)} items")
    
    # Step 2: Fetch and parse the first item's nutrition page
    base_url = "https://www.absecom.psu.edu/menus/user-pages/"
    first_item_url = base_url + nutrition_links[0]
    
    nutrition_response = session.get(first_item_url, headers=headers)
    print(f"Nutrition page length: {len(nutrition_response.text)}")
    print(f"B tag count: {nutrition_response.text.count('<b>')}")
    
    result = parse_nutrition_page(nutrition_response.text)
    for key, value in result.items():
        print(f"{key}: {value}")