import logging
import json
import os
from dotenv import dotenv_values

from .telegram_chat import TelegramBot
import requests
import cloudscraper

CITY_IDS = {
    "24": "Amsterdam",
    "320": "Arnhem",
    "619": "Capelle aan den IJssel",
    "26": "Delft",
    "28": "Den Bosch",
    "90": "Den Haag",
    "110": "Diemen",
    "620": "Dordrecht",
    "29": "Eindhoven",
    "545": "Groningen",
    "616": "Haarlem",
    "6099": "Helmond",
    "6209": "Maarssen",
    "6090": "Maastricht",
    "6051": "Nieuwegein",
    "6217": "Nijmegen",
    "25": "Rotterdam",
    "6224": "Rijswijk",
    "6211": "Sittard",
    "6093": "Tilburg",
    "27": "Utrecht",
    "6145": "Zeist",
    "6088": "Zoetermeer",
}

CONTRACT_TYPES = {
    "21": "Indefinite",
    "6125": "2 years",
    "20": "1 year max",
    "318": "6 months max",
    "606": "4 months max",
}

ROOM_TYPES = {
    "104": "Studio",
    "6137": "Loft (open bedroom area)",
    "105": "1",
    "106": "2",
    "108": "3",
    "382": "4",
}

MAX_REGISTER_TYPES = {
    "22": "One",
    "23": "Two (only couples)",
    "500": "Two",
    "380": "Family (parents with children)",
    "501": "Three",
    "502": "Four",
}

def city_id_to_city(city_id):
    return CITY_IDS.get(city_id)

def contract_type_id_to_str(contract_type_id):
    return CONTRACT_TYPES.get(contract_type_id, "Unknown")

def room_id_to_room(room_id):
    return ROOM_TYPES.get(room_id, "Unknown")

def max_register_id_to_str(maxregister_id):
    return MAX_REGISTER_TYPES.get(maxregister_id, "Unknown")

def url_key_to_link(url_key):
    return f"https://holland2stay.com/residences/{url_key}.html"

def clean_img(url):
    try:
        if 'cache' not in url:
            return url
        parts = url.split('/')
        ci = parts.index('cache')
        return '/'.join(parts[:ci] + parts[ci + 2:])
    except Exception as error:
        return url

def house_to_msg(house):
    return f"""
New house in #{city_id_to_city(house['city'])}!
{url_key_to_link(house['url_key'])}

Living area: {house['area']}m²
Price: {float(house['price_inc'].replace(',', '.')):,}€ (excl. {float(house['price_exc'].replace(',', '.')):,}€ basic rent)
Price per meter: {float(float(house['price_inc']) / float(house['area'])):.2f} €\\m²

Available from: {house['available_from']}
Bedrooms: {house['rooms']}
Max occupancy: {house['max_register']}
Contract type: {house['contract_type']}
<a href="https://holland2stay.com/rooms/{house['url_key']}">Apply here</a>
"""

# See details and apply on Holland2Stay website."""

def generate_payload(cities, page_size):
    return {
        "operationName": "GetCategories",
        "variables": {
            "currentPage": 1,
            "id": "Nw==",
            "filters": {
                "available_to_book": {"in": ["179", "336"]},
                "city": {"in": cities},
                "category_uid": {"eq": "Nw=="},
            },
            "pageSize": page_size,
            "sort": {"available_startdate": "ASC"},
        },
        "query": """
            query GetCategories($id: String!, $pageSize: Int!, $currentPage: Int!, $filters: ProductAttributeFilterInput!, $sort: ProductAttributeSortInput) {
              categories(filters: {category_uid: {in: [$id]}}) {
                items { uid __typename }
                __typename
              }
              products(
                pageSize: $pageSize
                currentPage: $currentPage
                filter: $filters
                sort: $sort
              ) {
                items {
                  name sku city url_key available_to_book available_startdate building_name
                  finishing living_area no_of_rooms resident_type offer_text_two offer_text
                  maximum_number_of_persons type_of_contract price_analysis_text allowance_price
                  floor basic_rent lumpsum_service_charge inventory caretaker_costs cleaning_common_areas
                  energy_common_areas allowance_price
                  media_gallery { url }
                  price_range {
                    maximum_price { final_price { value } }
                  }
                }
              }
            }
        """,
    }

def scrape(cities=["24", "25"], page_size=30, apikey=None, debug_chat_id=None):
    debug_telegram = TelegramBot(apikey=apikey, chat_id=debug_chat_id)
    payload = generate_payload(cities, page_size)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://holland2stay.com",
        "Referer": "https://holland2stay.com/"
    }

    scraper = cloudscraper.create_scraper()
    response = scraper.post("https://api.holland2stay.com/graphql/", json=payload, headers=headers)

    try:
        data = response.json()["data"]
    except Exception as e:
        debug_telegram.send_simple_msg(f"JSON解析失败: {str(e)}")
        logging.error(f"JSON解析失败: {str(e)}")
        return {}

    cities_dict = {c: [] for c in cities}
    MAX_BASIC_RENT = 900  # 你想设置的 basic rent 上限
    for house in data.get("products", {}).get("items", []):
        try:
            basic_rent = float(house["basic_rent"])
            if basic_rent > MAX_BASIC_RENT:
                continue  # 超过上限就跳过
            city_id = str(house["city"])
            cleaned_images = [clean_img(img['url']) for img in house.get('media_gallery', [])]
            cleaned_images = list(filter(lambda x: "logo-blue-1.jpg" not in x, cleaned_images))
            # 加这一句只保留第一张图，或干脆不存
            if cleaned_images:
                cleaned_images = [cleaned_images[0]]
            else:
                cleaned_images = []
            cities_dict[city_id].append({
                "url_key": house["url_key"],
                "city": city_id,
                "area": str(house["living_area"]).replace(",", "."),
                "price_exc": str(house["basic_rent"]),
                "price_inc": str(house["price_range"]["maximum_price"]["final_price"]["value"]),
                "available_from": house["available_startdate"],
                "max_register": str(max_register_id_to_str(str(house["maximum_number_of_persons"]))),
                "contract_type": contract_type_id_to_str(str(house["type_of_contract"])),
                "rooms": room_id_to_room(str(house["no_of_rooms"])),
                "images": cleaned_images
            })
        except Exception as err:
            debug_telegram.send_simple_msg(f"解析房屋时出错: {str(err)}")
            logging.error(f"解析房屋时出错: {str(err)}")
        finally:
            del response
            del scraper
            gc.collect()

    return cities_dict
