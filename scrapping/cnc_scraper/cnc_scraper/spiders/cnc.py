import scrapy
import os
import csv
import re
from datetime import datetime
import pandas as pd


class CNCSpider(scrapy.Spider):
    name = 'cnc'
    start_urls = ['https://www.cnc.fr/cinema/etudes-et-rapports/statistiques/frequentation-cinematographique']

    def __init__(self, *args, **kwargs):
        super(CNCSpider, self).__init__(*args, **kwargs)
        print("### INITIALISATION DU SPIDER ###")
        self.base_dir = 'cnc_data'
        self.frequentation_dir = os.path.join(self.base_dir, 'frequentation')
        self.parts_marche_dir = os.path.join(self.base_dir, 'parts_marche')

        print(f"Création des répertoires: {self.base_dir}, {self.frequentation_dir}, {self.parts_marche_dir}")
        os.makedirs(self.frequentation_dir, exist_ok=True)
        os.makedirs(self.parts_marche_dir, exist_ok=True)
        print("Initialisation des fichiers CSV...")
        self.init_csv_files()
        print("### INITIALISATION TERMINÉE ###")

    def init_csv_files(self):
        self.frequentation_file = os.path.join(self.frequentation_dir, 'frequentation_data.csv')
        with open(self.frequentation_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date Article', 'Période', 'Année Courante', 'Année Précédente', 'Évolution (%)'])
            print(f"Fichier créé: {self.frequentation_file}")

        self.parts_marche_file = os.path.join(self.parts_marche_dir, 'parts_marche_data.csv')
        with open(self.parts_marche_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date Article', 'Période',
                            'Films Français Année Courante', 'Films Français Année Précédente',
                            'Films Américains Année Courante', 'Films Américains Année Précédente',
                            'Autres Films Année Courante', 'Autres Films Année Précédente'])
            print(f"Fichier créé: {self.parts_marche_file}")

    def parse(self, response):
        print("\n### ANALYSE DE LA PAGE PRINCIPALE ###")
        print(f"URL en cours d'analyse: {response.url}")
        print(f"Status code: {response.status}")
        print(f"Taille de la réponse: {len(response.body)} octets")

        print("Recherche des articles avec différents sélecteurs CSS...")
        articles_card_body = response.css('div.card-body a::attr(href)').getall()
        articles_card = response.css('a.card::attr(href)').getall()
        articles_article = response.css('article a::attr(href)').getall()

        print(f"Sélecteur 'div.card-body a::attr(href)': {len(articles_card_body)} articles trouvés")
        print(f"Sélecteur 'a.card::attr(href)': {len(articles_card)} articles trouvés")
        print(f"Sélecteur 'article a::attr(href)': {len(articles_article)} articles trouvés")

        # Utiliser le sélecteur qui a trouvé le plus d'articles
        articles = articles_article if len(articles_article) > 0 else (articles_card if len(articles_card) > 0 else articles_card_body)
        print(f"Nombre total d'articles trouvés: {len(articles)}")

        # Supprimer les doublons
        articles = list(set(articles))

        for article_url in articles:
            full_url = response.urljoin(article_url)
            print(f"Article trouvé: {full_url}")
            yield scrapy.Request(full_url, callback=self.parse_article)

        # Vérifier s'il y a une pagination
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page:
            next_url = response.urljoin(next_page)
            print(f"Page suivante trouvée: {next_url}")
            yield scrapy.Request(next_url, callback=self.parse)
        else:
            print("Pas de page suivante trouvée")

    def parse_article(self, response):
        print("\n### ANALYSE DE L'ARTICLE ###")
        print(f"URL de l'article: {response.url}")
        print(f"Status code: {response.status}")
        print(f"Taille de la réponse: {len(response.body)} octets")

        # Extraction de la date de l'article
        date_text = response.css('div.date::text').get()
        if date_text:
            date_text = date_text.strip()
            print(f"Texte de date trouvé: {date_text}")
            try:
                # Essayer de parser la date
                date_formats = [
                    '%d %B %Y',  # 01 janvier 2023
                    '%d/%m/%Y',  # 01/01/2023
                ]

                article_date = None
                for date_format in date_formats:
                    try:
                        article_date = datetime.strptime(date_text, date_format).strftime('%Y-%m-%d')
                        break
                    except ValueError:
                        continue

                if article_date:
                    print(f"Date formatée: {article_date}")
                else:
                    print(f"Format de date non reconnu, utilisation du texte brut: {date_text}")
                    article_date = date_text
            except Exception as e:
                print(f"Erreur lors du parsing de la date: {e}")
                article_date = date_text
        else:
            print("Aucune date trouvée dans l'article")
            article_date = "Date inconnue"

        # Traiter tous les tableaux de l'article
        tables = response.css('table')
        print(f"Nombre de tableaux trouvés dans l'article: {len(tables)}")

        for i, table in enumerate(tables):
            print(f"\n--- Analyse du tableau {i+1}/{len(tables)} ---")

            # Afficher la structure HTML du tableau pour le débogage
            print(f"Structure HTML du tableau {i+1}:")
            table_html = table.get()
            print(table_html[:500] + "..." if len(table_html) > 500 else table_html)

            # Vérifier si c'est un tableau de parts de marché
            header_text = ''.join(table.css('thead *::text').getall()).lower()
            print(f"Texte d'en-tête: {header_text}")

            if 'parts de marché' in header_text:
                print(f"Tableau de parts de marché identifié (tableau {i+1})")
                self.extract_parts_marche_data(table, article_date)
            elif i == 0:  # Le premier tableau est généralement celui de fréquentation
                print(f"Traitement du tableau de fréquentation (tableau {i+1})")
                self.extract_frequentation_data(table, article_date)
            elif i == 1 and len(tables) >= 2:  # Le deuxième tableau pourrait être celui de parts de marché
                print(f"Traitement du tableau de parts de marché (tableau {i+1})")
                self.extract_parts_marche_data(table, article_date)

    def extract_frequentation_data(self, table, article_date):
        rows = table.css('tbody tr')
        print(f"Nombre de lignes dans le tableau de fréquentation: {len(rows)}")

        for row_index, row in enumerate(rows):
            cells = row.css('td')
            print(f"Ligne {row_index+1}: {len(cells)} cellules")

            if len(cells) >= 2:  # Au moins période et année courante
                try:
                    # Extraire le texte de la cellule de période
                    periode_text = cells[0].css('*::text').getall()
                    if not periode_text:
                        print(f"Aucun texte trouvé dans la cellule de période, ligne ignorée")
                        continue

                    periode = ''.join(periode_text).strip()
                    print(f"Période identifiée: '{periode}'")

                    # Extraire les valeurs des cellules
                    if len(cells) >= 4:  # Format avec évolution
                        annee_courante_text = cells[1].css('*::text').getall()
                        annee_precedente_text = cells[2].css('*::text').getall()
                        evolution_text = cells[3].css('*::text').getall() if len(cells) > 3 else []

                        annee_courante = ''.join(annee_courante_text).strip() if annee_courante_text else ""
                        annee_precedente = ''.join(annee_precedente_text).strip() if annee_precedente_text else ""
                        evolution = ''.join(evolution_text).strip() if evolution_text else ""
                    else:  # Format avec moins de colonnes
                        annee_courante_text = cells[1].css('*::text').getall()
                        annee_precedente_text = cells[2].css('*::text').getall() if len(cells) > 2 else []

                        annee_courante = ''.join(annee_courante_text).strip() if annee_courante_text else ""
                        annee_precedente = ''.join(annee_precedente_text).strip() if annee_precedente_text else ""
                        evolution = ""

                    print(f"Valeurs brutes: Année courante='{annee_courante}', Année précédente='{annee_precedente}', Évolution='{evolution}'")

                    # Nettoyer les données
                    annee_courante = re.sub(r'[^0-9,.]', '', annee_courante).replace(',', '.') if annee_courante else ""
                    annee_precedente = re.sub(r'[^0-9,.]', '', annee_precedente).replace(',', '.') if annee_precedente else ""
                    evolution = re.sub(r'[^0-9,.+-]', '', evolution).replace(',', '.') if evolution else ""

                    print(f"Valeurs nettoyées: Année courante='{annee_courante}', Année précédente='{annee_precedente}', Évolution='{evolution}'")

                    # Enregistrer les données
                    with open(self.frequentation_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([article_date, periode, annee_courante, annee_precedente, evolution])
                        print(f"Ligne ajoutée au fichier de fréquentation: {article_date}, {periode}, {annee_courante}, {annee_precedente}, {evolution}")
                except Exception as e:
                    print(f"Erreur lors de l'extraction de la fréquentation: {e}")
                    import traceback
                    print(traceback.format_exc())
            else:
                print(f"Ligne ignorée: nombre insuffisant de cellules ({len(cells)})")

    def extract_parts_marche_data(self, table, article_date):
        # Analyser l'en-tête pour comprendre la structure du tableau
        header_rows = table.css('thead tr')
        header_structure = []
        years = []

        print(f"Nombre de lignes d'en-tête: {len(header_rows)}")

        for i, header_row in enumerate(header_rows):
            header_cells = header_row.css('td, th')
            header_texts = []
            for cell in header_cells:
                cell_text = ''.join(cell.css('*::text').getall()).strip()
                header_texts.append(cell_text)

                # Essayer d'extraire les années
                if re.match(r'^\d{4}$', cell_text):
                    years.append(cell_text)

            print(f"En-tête ligne {i+1}: {header_texts}")
            header_structure.append(header_texts)

        # Déterminer les années courante et précédente
        annee_courante = years[0] if len(years) > 0 else ""
        annee_precedente = years[1] if len(years) > 1 else ""
        print(f"Années identifiées: courante={annee_courante}, précédente={annee_precedente}")

        # Analyser les lignes du tableau
        rows = table.css('tbody tr')
        print(f"Nombre de lignes dans le tableau de parts de marché: {len(rows)}")

        # Vérifier si le tableau a une structure spéciale (comme dans l'exemple de janvier 2024)
        special_structure = False
        if len(rows) > 0:
            first_cell_text = ''.join(rows[0].css('td:first-child *::text').getall()).strip().lower()
            if 'films français' in first_cell_text or 'films américains' in first_cell_text or 'autres films' in first_cell_text:
                special_structure = True
                print("Structure spéciale détectée (catégories de films en première colonne)")

        if special_structure:
            # Traitement pour les tableaux avec structure spéciale
            categories = []
            values_by_category = {}

            for row_index, row in enumerate(rows):
                cells = row.css('td')
                if len(cells) < 2:
                    continue

                category_text = ''.join(cells[0].css('*::text').getall()).strip().lower()
                print(f"Catégorie: {category_text}")

                if 'films français' in category_text:
                    category = 'films français'
                elif 'films américains' in category_text:
                    category = 'films américains'
                elif 'autres films' in category_text:
                    category = 'autres films'
                else:
                    category = category_text

                categories.append(category)

                # Extraire les valeurs
                values = []
                for cell_index, cell in enumerate(cells[1:]):
                    cell_text = ''.join(cell.css('*::text').getall()).strip()
                    values.append(cell_text)
                    print(f"Valeur pour {category}, cellule {cell_index+1}: {cell_text}")

                values_by_category[category] = values

            # Enregistrer les données par catégorie
            for category in categories:
                values = values_by_category.get(category, [])
                cleaned_values = []

                for value in values:
                    if value:
                        cleaned_value = re.sub(r'[^0-9,.]', '', value).replace(',', '.')
                        cleaned_values.append(cleaned_value)
                    else:
                        cleaned_values.append("")

                # Compléter avec des valeurs vides si nécessaire
                while len(cleaned_values) < 6:
                    cleaned_values.append("")

                with open(self.parts_marche_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    row_data = [article_date, category] + cleaned_values[:6]
                    writer.writerow(row_data)
                    print(f"Ligne ajoutée au fichier de parts de marché: {row_data}")
        else:
            # Traitement standard pour les tableaux avec périodes
            for row_index, row in enumerate(rows):
                cells = row.css('td')
                print(f"Ligne {row_index+1}: {len(cells)} cellules")

                if len(cells) < 2:
                    print(f"Ligne ignorée: nombre insuffisant de cellules ({len(cells)})")
                    continue

                try:
                    # Extraire le texte de la première cellule (période ou vide)
                    periode_texts = cells[0].css('*::text').getall()
                    periode = ''.join(periode_texts).strip() if periode_texts else f"Ligne {row_index+1}"

                    # Ignorer les lignes d'en-tête qui pourraient être dans le corps du tableau
                    # et ignorer également les lignes contenant "Ligne 1"
                    if not periode or periode == "" or periode.lower() in ["", "année courante", "année précédente"] or "Ligne 1" in periode:
                        print(f"Ligne ignorée: période vide, en-tête ou 'Ligne 1'")
                        continue

                    print(f"Période identifiée: '{periode}'")

                    # Extraire les valeurs des cellules
                    values = []
                    for cell_index, cell in enumerate(cells[1:]):
                        cell_texts = cell.css('*::text').getall()
                        value = ''.join(cell_texts).strip() if cell_texts else ""
                        print(f"Cellule {cell_index+1}: '{value}'")
                        values.append(value)

                    # Nettoyer les valeurs
                    cleaned_values = []
                    for value in values:
                        if value:
                            cleaned_value = re.sub(r'[^0-9,.]', '', value).replace(',', '.')
                            cleaned_values.append(cleaned_value)
                        else:
                            cleaned_values.append("")

                    print(f"Valeurs nettoyées: {cleaned_values}")

                    # Compléter avec des valeurs vides si nécessaire
                    while len(cleaned_values) < 6:
                        cleaned_values.append("")

                    # Enregistrer les données
                    with open(self.parts_marche_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        row_data = [article_date, periode] + cleaned_values[:6]
                        writer.writerow(row_data)
                        print(f"Ligne ajoutée au fichier de parts de marché: {row_data}")
                except Exception as e:
                    print(f"Erreur lors de l'extraction des parts de marché: {e}")
                    import traceback
                    print(traceback.format_exc())

