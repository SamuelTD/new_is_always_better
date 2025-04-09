# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
from datetime import datetime

class ImdbCleaningPipeline:
    """Pipeline pour nettoyer et normaliser les données des films"""

    def process_item(self, item, spider):
        # Nettoyer le titre (supprimer les espaces supplémentaires)
        if 'title' in item and item['title']:
            item['title'] = item['title'].strip()

        # Convertir l'année en entier
        if 'year' in item and item['year']:
            # Extraire seulement les chiffres
            year_match = re.search(r'(\d{4})', str(item['year']))
            if year_match:
                item['year'] = int(year_match.group(1))
            else:
                item['year'] = None

        # Convertir la durée en minutes (entier)
        if 'runtime' in item and item['runtime']:
            if isinstance(item['runtime'], str):
                # Si c'est une chaîne comme "2h 30min", extraire les minutes
                hours = re.search(r'(\d+)h', item['runtime'])
                minutes = re.search(r'(\d+)m', item['runtime'])
                total_minutes = 0
                if hours:
                    total_minutes += int(hours.group(1)) * 60
                if minutes:
                    total_minutes += int(minutes.group(1))
                item['runtime'] = total_minutes if total_minutes > 0 else None

        # Convertir la note en nombre flottant
        if 'rating' in item and item['rating']:
            try:
                item['rating'] = float(str(item['rating']).replace(',', '.'))
            except (ValueError, TypeError):
                item['rating'] = None

        # Convertir les votes en entier
        if 'votes' in item and item['votes']:
            if isinstance(item['votes'], str):
                # Supprimer les caractères non numériques (comme "K", "M", parenthèses, virgules)
                votes_clean = re.sub(r'[^\d]', '', item['votes'])
                if votes_clean:
                    item['votes'] = int(votes_clean)
                else:
                    item['votes'] = None

        # Normaliser les URLs
        if 'url' in item and item['url']:
            # S'assurer que l'URL commence par http ou https
            if item['url'] and not item['url'].startswith(('http://', 'https://')):
                item['url'] = 'https://www.imdb.com' + item['url']

        if 'image_url' in item and item['image_url']:
            # S'assurer que l'URL de l'image est complète
            if item['image_url'] and not item['image_url'].startswith(('http://', 'https://')):
                item['image_url'] = 'https:' + item['image_url']

        # Ajouter un timestamp de scraping
        item['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return item
