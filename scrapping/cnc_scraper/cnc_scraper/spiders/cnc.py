import scrapy
import os
import csv
import re
from datetime import datetime
import locale  # Importer le module locale


class CncSpider(scrapy.Spider):
    name = 'cnc'
    start_urls = ['https://www.cnc.fr/cinema/etudes-et-rapports/statistiques/frequentation-cinematographique']

    custom_settings = {
        'TARGET_YEAR': 2010,  # Scrape data back to 2010
        'DOWNLOAD_DELAY': 1,  # Add a delay between requests to be respectful
    }

    def __init__(self, *args, **kwargs):
        super(CncSpider, self).__init__(*args, **kwargs)
        print("### INITIALISATION DU SPIDER ###")
        self.base_dir = 'cnc_data'
        self.frequentation_dir = os.path.join(self.base_dir, 'frequentation')
        self.parts_marche_dir = os.path.join(self.base_dir, 'parts_marche')

        self.target_year = self.custom_settings.get('TARGET_YEAR', 2010)

        os.makedirs(self.frequentation_dir, exist_ok=True)
        os.makedirs(self.parts_marche_dir, exist_ok=True)

        self.init_csv_files()
        self.visited_urls = set()

        # Configurer la langue en français pour gérer les dates
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

        print("### INITIALISATION TERMINÉE ###")

    def init_csv_files(self):
        print("### INITIALISATION DES FICHIERS CSV ###")
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
        print(f"### ANALYSE DE LA PAGE PRINCIPALE ###")
        print(f"URL en cours d'analyse: {response.url}")

        articles = response.css('div.journal-content-article a::attr(href)').getall()
        articles = list(set(articles))
        print(f"Nombre total d'articles trouvés: {len(articles)}")

        for article_url in articles:
            full_url = response.urljoin(article_url)
            if full_url in self.visited_urls:
                print(f"Article déjà visité: {full_url}")
                continue
            self.visited_urls.add(full_url)
            print(f"Article trouvé: {full_url}")
            yield scrapy.Request(full_url, callback=self.parse_article)

        next_page = response.css('ul.lfr-pagination-buttons li a.navigation.next::attr(href)').get()
        if next_page and not next_page.startswith('javascript:'):
            next_url = response.urljoin(next_page)
            print(f"Page suivante trouvée: {next_url}")
            yield scrapy.Request(next_url, callback=self.parse)
        else:
            print("Pas de page suivante trouvée ou lien invalide.")

    def parse_article(self, response):
        print(f"### ANALYSE DE L'ARTICLE ###")
        print(f"URL de l'article: {response.url}")

        # Extraction de la date de l'article
        date_text = response.css('div.date::text').get()
        if date_text:
            date_text = date_text.strip()
            try:
                # Convertir la date en format standard (YYYY-MM-DD)
                article_date = datetime.strptime(date_text, '%d %B %Y').strftime('%Y-%m-%d')
                print(f"Date de l'article extraite : {article_date}")
            except ValueError:
                print(f"Format de date invalide : {date_text}")
                article_date = "Date inconnue"
        else:
            article_date = "Date inconnue"
            print("Date de l'article non trouvée.")

        # Vérifier si l'année de l'article est plus récente que l'année cible
        if article_date != "Date inconnue":
            article_year = int(article_date.split('-')[0])
            if article_year < self.target_year:
                print(f"Article ignoré car l'année ({article_year}) est plus ancienne que l'année cible ({self.target_year}).")
                return

        # Traiter tous les tableaux de l'article
        tables = response.css('table')
        print(f"Nombre de tableaux trouvés dans l'article: {len(tables)}")

        for i, table in enumerate(tables):
            header_text = ''.join(table.css('thead *::text').getall()).lower()
            print(f"Analyse du tableau {i + 1} avec en-tête : {header_text}")
            if 'parts de marché' in header_text:
                self.extract_parts_marche_data(table, article_date)
            elif i == 0:  # Le premier tableau est généralement celui de fréquentation
                self.extract_frequentation_data(table, article_date)

    def extract_frequentation_data(self, table, article_date):
        print(f"### EXTRACTION DES DONNÉES DE FRÉQUENTATION POUR L'ARTICLE : {article_date} ###")
        tbodies = table.css('tbody')
        if not tbodies:
            print(f"Aucun <tbody> trouvé dans le tableau de fréquentation pour l'article : {article_date}")
            return

        for tbody in tbodies:
            rows = tbody.css('tr')
            if not rows:  # Ignorer les <tbody> vides
                print(f"<tbody> vide ignoré pour l'article : {article_date}")
                continue

            for row in rows:
                cells = row.css('td')
                if len(cells) >= 4:
                    # Extraire le texte en combinant plusieurs sélecteurs
                    periode = ''.join(cells[0].css('*::text, span::text, div::text').getall()).strip()
                    annee_courante = ''.join(cells[1].css('*::text, span::text, div::text').getall()).strip()
                    annee_precedente = ''.join(cells[2].css('*::text, span::text, div::text').getall()).strip()
                    evolution = ''.join(cells[3].css('*::text, span::text, div::text').getall()).strip()

                    print(f"Extrait : Période={periode}, Année Courante={annee_courante}, Année Précédente={annee_precedente}, Évolution={evolution}")

                    # Nettoyer les données
                    periode = re.sub(r'\s+', ' ', periode).strip() if periode else "Période inconnue"
                    annee_courante = re.sub(r'[^0-9,.]', '', annee_courante).replace(',', '.') if annee_courante else "0"
                    annee_precedente = re.sub(r'[^0-9,.]', '', annee_precedente).replace(',', '.') if annee_precedente else "0"
                    evolution = re.sub(r'[^0-9,.+-]', '', evolution).replace(',', '.') if evolution else "0"

                    # Enregistrer les données
                    with open(self.frequentation_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([article_date, periode, annee_courante, annee_precedente, evolution])

    def extract_parts_marche_data(self, table, article_date):
        print(f"### EXTRACTION DES DONNÉES DE PARTS DE MARCHÉ POUR L'ARTICLE : {article_date} ###")

        # Récupérer tous les <tbody> dans le tableau
        tbodies = table.css('tbody')
        if not tbodies:
            print(f"Aucun <tbody> trouvé dans le tableau des parts de marché pour l'article : {article_date}")
            return

        for tbody in tbodies:
            rows = tbody.css('tr')
            if not rows:  # Ignorer les <tbody> vides
                print(f"<tbody> vide ignoré pour l'article : {article_date}")
                continue

            # Vérifier si le tableau a une structure avec des colonnes fusionnées
            header_row = rows[0].css('td, th')
            if len(header_row) >= 7 and 'Films français' in ''.join(header_row.css('*::text').getall()):
                print("Structure de tableau avec colonnes fusionnées détectée.")
                self.extract_parts_marche_data_colspan(rows, article_date)
                return

            # Si la structure est classique, continuer avec l'extraction normale
            for row in rows:
                cells = row.css('td')
                if len(cells) >= 7:
                    # Extraire le texte en combinant plusieurs sélecteurs
                    periode = ''.join(cells[0].css('*::text, span::text, div::text').getall()).strip()
                    films_francais_courant = ''.join(cells[1].css('*::text, span::text, div::text').getall()).strip()
                    films_francais_precedent = ''.join(cells[2].css('*::text, span::text, div::text').getall()).strip()
                    films_americains_courant = ''.join(cells[3].css('*::text, span::text, div::text').getall()).strip()
                    films_americains_precedent = ''.join(cells[4].css('*::text, span::text, div::text').getall()).strip()
                    autres_films_courant = ''.join(cells[5].css('*::text, span::text, div::text').getall()).strip()
                    autres_films_precedent = ''.join(cells[6].css('*::text, span::text, div::text').getall()).strip()

                    print(f"Extrait brut : Période={periode}, "
                        f"Films Français={films_francais_courant}/{films_francais_precedent}, "
                        f"Films Américains={films_americains_courant}/{films_americains_precedent}, "
                        f"Autres Films={autres_films_courant}/{autres_films_precedent}")

                    # Nettoyer les données
                    periode = re.sub(r'\s+', ' ', periode).strip() if periode else "Période inconnue"
                    films_francais_courant = re.sub(r'[^0-9,.]', '', films_francais_courant).replace(',', '.') if films_francais_courant else "0"
                    films_francais_precedent = re.sub(r'[^0-9,.]', '', films_francais_precedent).replace(',', '.') if films_francais_precedent else "0"
                    films_americains_courant = re.sub(r'[^0-9,.]', '', films_americains_courant).replace(',', '.') if films_americains_courant else "0"
                    films_americains_precedent = re.sub(r'[^0-9,.]', '', films_americains_precedent).replace(',', '.') if films_americains_precedent else "0"
                    autres_films_courant = re.sub(r'[^0-9,.]', '', autres_films_courant).replace(',', '.') if autres_films_courant else "0"
                    autres_films_precedent = re.sub(r'[^0-9,.]', '', autres_films_precedent).replace(',', '.') if autres_films_precedent else "0"

                    print(f"Données nettoyées : Période={periode}, "
                        f"Films Français={films_francais_courant}/{films_francais_precedent}, "
                        f"Films Américains={films_americains_courant}/{films_americains_precedent}, "
                        f"Autres Films={autres_films_courant}/{autres_films_precedent}")

                    # Enregistrer les données
                    with open(self.parts_marche_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([article_date, periode, films_francais_courant, films_francais_precedent,
                                        films_americains_courant, films_americains_precedent,
                                        autres_films_courant, autres_films_precedent])
                else:
                    print(f"Ligne ignorée : Pas assez de colonnes (trouvé {len(cells)} colonnes).")

    def extract_parts_marche_data_colspan(self, rows, article_date):
        """
        Méthode pour extraire les données des tableaux avec colonnes fusionnées (colspan).
        """
        print(f"### EXTRACTION DES DONNÉES AVEC COLSPAN POUR L'ARTICLE : {article_date} ###")

        for row in rows[2:]:  # Ignorer les deux premières lignes d'en-tête
            cells = row.css('td')
            if len(cells) >= 7:
                periode = ''.join(cells[0].css('*::text, span::text, div::text').getall()).strip()
                films_francais_courant = ''.join(cells[1].css('*::text, span::text, div::text').getall()).strip()
                films_francais_precedent = ''.join(cells[2].css('*::text, span::text, div::text').getall()).strip()
                films_americains_courant = ''.join(cells[3].css('*::text, span::text, div::text').getall()).strip()
                films_americains_precedent = ''.join(cells[4].css('*::text, span::text, div::text').getall()).strip()
                autres_films_courant = ''.join(cells[5].css('*::text, span::text, div::text').getall()).strip()
                autres_films_precedent = ''.join(cells[6].css('*::text, span::text, div::text').getall()).strip()

                print(f"Extrait brut (colspan) : Période={periode}, "
                    f"Films Français={films_francais_courant}/{films_francais_precedent}, "
                    f"Films Américains={films_americains_courant}/{films_americains_precedent}, "
                    f"Autres Films={autres_films_courant}/{autres_films_precedent}")

                # Nettoyer les données
                periode = re.sub(r'\s+', ' ', periode).strip() if periode else "Période inconnue"
                films_francais_courant = re.sub(r'[^0-9,.]', '', films_francais_courant).replace(',', '.') if films_francais_courant else "0"
                films_francais_precedent = re.sub(r'[^0-9,.]', '', films_francais_precedent).replace(',', '.') if films_francais_precedent else "0"
                films_americains_courant = re.sub(r'[^0-9,.]', '', films_americains_courant).replace(',', '.') if films_americains_courant else "0"
                films_americains_precedent = re.sub(r'[^0-9,.]', '', films_americains_precedent).replace(',', '.') if films_americains_precedent else "0"
                autres_films_courant = re.sub(r'[^0-9,.]', '', autres_films_courant).replace(',', '.') if autres_films_courant else "0"
                autres_films_precedent = re.sub(r'[^0-9,.]', '', autres_films_precedent).replace(',', '.') if autres_films_precedent else "0"

                print(f"Données nettoyées (colspan) : Période={periode}, "
                    f"Films Français={films_francais_courant}/{films_francais_precedent}, "
                    f"Films Américains={films_americains_courant}/{films_americains_precedent}, "
                    f"Autres Films={autres_films_courant}/{autres_films_precedent}")

                # Enregistrer les données
                with open(self.parts_marche_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([article_date, periode, films_francais_courant, films_francais_precedent,
                                    films_americains_courant, films_americains_precedent,
                                    autres_films_courant, autres_films_precedent])