import scrapy
import random
import datetime
import pandas as pd
from scrapy import signals


class ImdbSpiderSpider(scrapy.Spider):
    name = "imdb_spider"
    allowed_domains = ["imdb.com"]

    # Paramètres configurables
    years_back = 2
    max_pages_per_year = 600

    # Nom du fichier de sortie
    output_file = "imdb_movies.csv"

    # Liste d'User-Agents pour rotation
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0'
    ]

    def __init__(self, years_back=None, max_pages=None, output_file=None, *args, **kwargs):
        super(ImdbSpiderSpider, self).__init__(*args, **kwargs)
        # Permettre de configurer les paramètres via la ligne de commande
        if years_back:
            self.years_back = int(years_back)
        if max_pages:
            self.max_pages_per_year = int(max_pages)
        if output_file:
            self.output_file = output_file

        # Calculer les années à scraper
        current_year = datetime.datetime.now().year
        self.years_to_scrape = list(range(current_year - self.years_back + 1, current_year + 1))

        self.logger.info(f"Spider configuré pour scraper les années: {self.years_to_scrape}")
        self.logger.info(f"Maximum de {self.max_pages_per_year} pages par année")
        self.logger.info(f"Les données seront sauvegardées dans: {self.output_file}")

        # Liste pour stocker tous les éléments
        self.all_items = []

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(ImdbSpiderSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self, spider):
        """Méthode appelée lorsque le spider termine son exécution"""
        self.logger.info("Spider terminé, sauvegarde des données en CSV...")

        if self.all_items:
            # Convertir en DataFrame et sauvegarder en CSV
            df = pd.DataFrame(self.all_items)
            df.to_csv(self.output_file, index=False)
            self.logger.info(f"Données sauvegardées dans {self.output_file} ({len(self.all_items)} films)")
        else:
            self.logger.warning("Aucune donnée à sauvegarder")

    def start_requests(self):
        for year in self.years_to_scrape:
            # URL pour chaque année
            url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={year}-01-01,{year}-12-31&genres=!documentary,!short&sort=release_date,desc"
            # Rotation d'User-Agent
            headers = {'User-Agent': random.choice(self.user_agents)}

            self.logger.info(f"Démarrage du scraping pour l'année {year}")

            yield scrapy.Request(
                url=url,
                callback=self.parse,
                headers=headers,
                meta={'year': year, 'page': 1}
            )

    def parse(self, response):
        # Nouveaux sélecteurs basés sur l'HTML fourni
        movies = response.css('div.ipc-metadata-list-summary-item__c')

        self.logger.info(f"Scraping de {len(movies)} films sur la page {response.meta['page']} pour l'année {response.meta['year']}")

        for movie in movies:
            # TITRE - Nouveau sélecteur
            title = movie.css('h3.ipc-title__text::text').get()
            if title and '. ' in title:  # Supprimer le numéro au début
                title = title.split('. ', 1)[1]

            # ANNÉE - Nouveau sélecteur
            year_text = movie.css('span.dli-title-metadata-item:nth-child(1)::text').get()
            year = year_text.strip() if year_text else None

            # DURÉE - Nouveau sélecteur
            runtime_text = movie.css('span.dli-title-metadata-item:nth-child(2)::text').get()
            runtime = None
            if runtime_text:
                # Extraire seulement les minutes (format: "1h 34m")
                parts = runtime_text.split()
                runtime = 0
                for part in parts:
                    if 'h' in part:
                        runtime += int(part.replace('h', '')) * 60
                    elif 'm' in part:
                        runtime += int(part.replace('m', ''))

            # NOTE IMDb - Nouveau sélecteur
            rating = movie.css('span.ipc-rating-star--imdb-rating span.ipc-rating-star--rating::text').get()

            # VOTES - Nouveau sélecteur
            votes_text = movie.css('span.ipc-rating-star--voteCount::text').get()
            votes = None
            if votes_text:
                # Nettoyer le format "(119)" pour obtenir juste le nombre
                votes = votes_text.strip().strip('()').replace(',', '')

            # URL DU FILM - Nouveau sélecteur
            movie_url = movie.css('a.ipc-title-link-wrapper::attr(href)').get()
            if movie_url:
                movie_url = response.urljoin(movie_url)

            # IMAGE DU FILM - Nouveau sélecteur
            image_url = movie.css('img.ipc-image::attr(src)').get()

            item = {
                'title': title,
                'year': year,
                'runtime': runtime,
                'rating': rating,
                'votes': votes,
                'url': movie_url,
                'image_url': image_url,
                'scrape_year': response.meta['year']
            }

            # Ajouter à la liste globale
            self.all_items.append(item)

            # Yield pour le pipeline Scrapy standard
            yield item

        # PAGINATION - Sélecteur corrigé pour le bouton "50 en plus" avec prints de débogage
        pagination_container = response.css('div.sc-f09bd1f5-1.hoKmdt.pagination-container, div.pagination-container')
        print(f"DEBUG PAGINATION: Container trouvé: {bool(pagination_container)}")

        if pagination_container and response.meta['page'] < self.max_pages_per_year:
            # Chercher le bouton "50 en plus" dans le conteneur de pagination
            see_more_button = pagination_container.css('span.single-page-see-more-button button, span.ipc-see-more button')
            print(f"DEBUG PAGINATION: Bouton '50 en plus' trouvé: {bool(see_more_button)}")

            if see_more_button:
                # Trouver l'URL de la page suivante en modifiant l'URL actuelle
                current_url = response.url
                print(f"DEBUG PAGINATION: URL actuelle: {current_url}")

                # Vérifier si l'URL contient déjà un paramètre start
                if 'start=' in current_url:
                    # Si oui, incrémenter la valeur de start de 50
                    import re
                    current_start = int(re.search(r'start=(\d+)', current_url).group(1))
                    next_start = current_start + 50
                    next_page_url = re.sub(r'start=\d+', f'start={next_start}', current_url)
                    print(f"DEBUG PAGINATION: Paramètre start trouvé, incrémenté à {next_start}")
                else:
                    # Si non, ajouter &start=51 à l'URL
                    next_page_url = current_url + '&start=51'
                    print(f"DEBUG PAGINATION: Paramètre start non trouvé, ajout de &start=51")

                print(f"DEBUG PAGINATION: URL de la page suivante: {next_page_url}")
                self.logger.info(f"Passage à la page {response.meta['page'] + 1} pour l'année {response.meta['year']}")
                self.logger.info(f"URL de la page suivante: {next_page_url}")

                # Rotation d'User-Agent
                headers = {'User-Agent': random.choice(self.user_agents)}
                print(f"DEBUG PAGINATION: User-Agent: {headers['User-Agent']}")

                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                    headers=headers,
                    meta={
                        'year': response.meta['year'],
                        'page': response.meta['page'] + 1
                    }
                )
            else:
                print(f"DEBUG PAGINATION: Bouton '50 en plus' NON TROUVÉ pour l'année {response.meta['year']}")
                self.logger.warning(f"Bouton '50 en plus' non trouvé pour l'année {response.meta['year']}")
        else:
            print(f"DEBUG PAGINATION: Conteneur de pagination non trouvé OU limite de pages atteinte ({response.meta['page']} >= {self.max_pages_per_year})")
            self.logger.warning(f"Conteneur de pagination non trouvé ou limite de pages atteinte pour l'année {response.meta['year']}")