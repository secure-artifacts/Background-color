import os
import json
import requests
import threading
from PIL import Image

class DataManager:
    def __init__(self):
        self.cache_dir = "cache"
        self.data_file = "color_data.json"
        self.favorites_file = "favorites.json"
        
        # Ensure cache directory exists
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.data = self.load_data()
        self.favorites = self.load_favorites()
        
        # English to Chinese mappings from the website
        self.category_names = {
            '3D': '3D',
            'illustration': '插画',
            'pureColor': '纯色',
            'animal': '动物',
            'landscape': '风景',
            'flower': '花朵',
            'texture': '纹理',
            'gradient': '渐变',
            'festival': '节日',
            'other': '其它',
            'food': '食物',
            'fruit': '水果',
            'sport': '体育',
            'pattern': '图案',
            'messageBubble': '消息气泡',
            'heartPattern': '心形图案',
            'starrySky': '星空',
            'virtualAvatar': '虚拟形象',
            'plant': '植物'
        }

    def fetch_latest_data(self):
        """Fetches the latest data from the URL on a background thread."""
        try:
            response = requests.get("https://raz1ner.com/Extension/Background-Color-Post/color.json", timeout=10)
            if response.status_code == 200:
                self.data = response.json()
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, ensure_ascii=False, indent=2)
                return True
        except Exception as e:
            print(f"Failed to fetch data: {e}")
        return False

    def load_data(self):
        """Loads cached data if available."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def load_favorites(self):
        """Loads user favorites."""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def save_favorites(self):
        """Saves current favorites list."""
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.favorites), f, ensure_ascii=False)

    def toggle_favorite(self, img_id):
        """Toggles an image's favorite status."""
        if img_id in self.favorites:
            self.favorites.remove(img_id)
            is_fav = False
        else:
            self.favorites.add(img_id)
            is_fav = True
        self.save_favorites()
        return is_fav

    def is_favorite(self, img_id):
        return img_id in self.favorites

    def get_category_name(self, cat_key):
        return self.category_names.get(cat_key, cat_key)

    def get_image_path(self, img_id):
        """Returns the local path to the image, downloading it if necessary."""
        cache_path = os.path.join(self.cache_dir, f"{img_id}.png")
        if os.path.exists(cache_path):
            return cache_path
            
        try:
            url = f"https://raz1ner.com/images/Background-Color/{img_id}-2x.png"
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(cache_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return cache_path
        except Exception as e:
            print(f"Error downloading image {img_id}: {e}")
        return None
