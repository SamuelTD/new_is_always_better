# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd 
import os

class CncScraperPipeline:
    def __init__(self):
        # Initialisation de la pipeline
        self.base_dir = 'cnc_data'
        self.frequentation_dir = os.path.join(self.base_dir, 'frequentation')
        self.parts_marche_dir = os.path.join(self.base_dir, 'parts_marche')

    def close_spider(self, spider):
        # Cette méthode est appelée quand le spider termine son exécution
        print("### CONVERSION DES FICHIERS CSV EN PARQUET ###")

        # Convertir le fichier de fréquentation
        frequentation_csv = os.path.join(self.frequentation_dir, 'frequentation_data.csv')
        frequentation_parquet = os.path.join(self.frequentation_dir, 'frequentation_data.parquet')

        if os.path.exists(frequentation_csv):
            try:
                print(f"Conversion de {frequentation_csv} en Parquet...")
                df_freq = pd.read_csv(frequentation_csv)
                df_freq.to_parquet(frequentation_parquet)
                print(f"Fichier Parquet créé: {frequentation_parquet}")
            except Exception as e:
                print(f"Erreur lors de la conversion du fichier de fréquentation: {e}")
        else:
            print(f"Fichier CSV de fréquentation non trouvé: {frequentation_csv}")

        # Convertir le fichier de parts de marché
        parts_marche_csv = os.path.join(self.parts_marche_dir, 'parts_marche_data.csv')
        parts_marche_parquet = os.path.join(self.parts_marche_dir, 'parts_marche_data.parquet')

        if os.path.exists(parts_marche_csv):
            try:
                print(f"Conversion de {parts_marche_csv} en Parquet...")
                df_parts = pd.read_csv(parts_marche_csv)
                df_parts.to_parquet(parts_marche_parquet)
                print(f"Fichier Parquet créé: {parts_marche_parquet}")
            except Exception as e:
                print(f"Erreur lors de la conversion du fichier de parts de marché: {e}")
        else:
            print(f"Fichier CSV de parts de marché non trouvé: {parts_marche_csv}")

        print("### CONVERSION TERMINÉE ###")