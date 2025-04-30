# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd


class JpboxofficePipeline:
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        adapter["amount_of_film_played_in"] = adapter["amount_of_film_played_in"].replace(" Films", "")
        
        adapter["boxoffice_average"] = adapter["boxoffice_average"].replace(" ", "")
        
        adapter["boxoffice_average_first_role"] = adapter["boxoffice_average_first_role"].replace(" ", "")
        
        adapter["boxoffice_total"] = adapter["boxoffice_total"].replace(" ", "")
        
        adapter["boxoffice_total_first_role"] = adapter["boxoffice_total_first_role"].replace(" ", "")
        
        if "Acteur " in adapter["nationality"]:
            adapter["nationality"] = adapter["nationality"].replace("Acteur ", "")
        
        if "Actrice " in adapter["nationality"]:
            adapter["nationality"] = adapter["nationality"].replace("Actrice ", "")

        adapter["rank"] = adapter["rank"].strip()
        
        return item

    def close_spider(self, spider):
        """
        On the spider closing, create a parquet file from the created .csv
        """
        
        df = pd.read_csv("./JpboxSpider.csv")
        df.to_parquet("JpboxSpider.parquet", index=False)