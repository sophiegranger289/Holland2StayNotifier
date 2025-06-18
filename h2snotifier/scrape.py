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
    response = None
    data = {}

    try:
        response = scraper.post("https://api.holland2stay.com/graphql/", json=payload, headers=headers)

        # 检查响应状态码
        if response.status_code != 200:
            debug_telegram.send_simple_msg(f"⚠️ 请求失败，状态码: {response.status_code}")
            debug_telegram.send_simple_msg(f"响应内容:\n{response.text[:300]}")
            logging.warning(f"请求失败，状态码: {response.status_code}")
            return {}

        # 检查是否为 JSON 响应
        if "application/json" not in response.headers.get("Content-Type", ""):
            debug_telegram.send_simple_msg("⚠️ 响应非 JSON，可能被 Cloudflare 拦截")
            debug_telegram.send_simple_msg(f"响应内容:\n{response.text[:300]}")
            logging.warning("响应不是JSON格式")
            return {}

        # 尝试解析 JSON
        try:
            data = response.json().get("data", {})
        except Exception as e:
            debug_telegram.send_simple_msg(f"❌ JSON解析失败: {str(e)}")
            debug_telegram.send_simple_msg(f"原始响应:\n{response.text[:300]}")
            logging.error(f"JSON解析失败: {str(e)}")
            return {}

    except Exception as e:
        debug_telegram.send_simple_msg(f"❌ 请求异常: {str(e)}")
        logging.error(f"请求异常: {str(e)}")
        return {}
    finally:
        if response is not None:
            del response
        del scraper
        gc.collect()

    # 开始处理数据
    cities_dict = {c: [] for c in cities}
    MAX_BASIC_RENT = 900
    for house in data.get("products", {}).get("items", []):
        try:
            basic_rent = float(house["basic_rent"])
            if basic_rent > MAX_BASIC_RENT:
                continue
            city_id = str(house["city"])
            cleaned_images = [clean_img(img['url']) for img in house.get('media_gallery', [])]
            cleaned_images = list(filter(lambda x: "logo-blue-1.jpg" not in x, cleaned_images))
            cleaned_images = [cleaned_images[0]] if cleaned_images else []
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
            debug_telegram.send_simple_msg(f"⚠️ 解析房屋数据失败: {str(err)}")
            logging.error(f"解析房屋数据失败: {str(err)}")
            continue

    return cities_dict
