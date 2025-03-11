#!/usr/bin/env python3
import emoji
import json
import re
import random
from render_emoji import render_emoji
import os
import sys
from PIL import Image

def get_average_rgb(image_path):
    if not os.path.exists(image_path):
        return None

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        pixels = list(img.getdata())
        return tuple(sum(c) // len(pixels) for c in zip(*pixels))

def generate_emoji_list():
    all_emojis = emoji.EMOJI_DATA
    emoji_list = []

    pictorial_categories = {
        'face', 'person', 'animal', 'food', 'plant', 'place',
        'transport', 'object', 'symbol', 'flag'
    }

    excluded_patterns = [
        r'^:[a-z0-9_\-]+:$',
        r'^\d+.*$',
        r'^[#*].*$',
        r'^[↖↙↗↘⬆⬇].*$',
    ]

    for emoji_char, data in all_emojis.items():
        if any(re.match(pattern, emoji_char) for pattern in excluded_patterns):
            continue

        if len(emoji_char) == 1 and ord(emoji_char) < 0x1F000:
            continue

        emoji_group = data.get('group', '').lower()
        is_pictorial = any(category in emoji_group for category in pictorial_categories)

        if not emoji_group or not is_pictorial:
            code_point = ord(emoji_char[0])
            is_pictorial = (0x1F300 <= code_point <= 0x1F9FF) or (0x2600 <= code_point <= 0x26FF)

        if is_pictorial:
            shortcode = data.get('en', '')
            clean_name = shortcode.strip(':')
            emoji_list.append({'emoji': emoji_char, 'name': clean_name})

    emoji_list.sort(key=lambda x: ord(x['emoji'][0]))
    return emoji_list

def save_emoji_list(emoji_list, filename='emoji_list.json', output_dir='emojis/', skip_render=False):
    os.makedirs(output_dir, exist_ok=True)

    for emoji_item in emoji_list:
        emoji_char = emoji_item['emoji']
        emoji_name = emoji_item['name'].replace(" ", "_")
        output_path = os.path.join(output_dir, f"{emoji_name}.png")

        if not skip_render:
            render_emoji(emoji_char, output_path)

        avg_rgb = get_average_rgb(output_path)
        emoji_item['rgb'] = avg_rgb
        print(f"Processed {emoji_char}: RGB={avg_rgb}")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(emoji_list, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(emoji_list)} emojis to {filename}")

def print_emoji_sample(emoji_list, count=10):
    print(f"Sample of {count} random emojis from the list:")
    sample_count = min(count, len(emoji_list))
    for i, emoji_item in enumerate(random.sample(emoji_list, sample_count)):
        print(f"{i+1}. {emoji_item['emoji']} - {emoji_item['name']}")

if __name__ == "__main__":
    skip_render = '--skip' in sys.argv
    emoji_list = generate_emoji_list()
    print(f"Total pictorial emojis found: {len(emoji_list)}")
    print_emoji_sample(emoji_list)
    save_emoji_list(emoji_list, skip_render=skip_render)