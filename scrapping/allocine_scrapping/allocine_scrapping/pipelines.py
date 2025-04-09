# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import pandas as pd

class AllocineScrappingPipeline:

    mois_fr_to_en = {
    'janvier': 'January', 'février': 'February', 'mars': 'March', 
    'avril': 'April', 'mai': 'May', 'juin': 'June', 
    'juillet': 'July', 'août': 'August', 'septembre': 'September', 
    'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        #Change comas to points in numeric fields
        coma_to_points = ['critics_score', 'viewers_score']
        for coma in coma_to_points:
            adapter[coma] = adapter[coma].replace(",", ".")

        #Remove uncessary text and white spaces
        adapter['french_boxoffice'] = adapter['french_boxoffice'].replace(" entrées", "").replace(" ", "")
                
        #Remove white spaces
        adapter['french_first_week_boxoffice'] = adapter['french_first_week_boxoffice'].replace(" ", "")
        
        #Convert the length of the movie to minutes if availlable.
        if adapter['length'] != "0" and adapter['length'] != "Date de sortie inconnue":
            adapter['length'] = self.hours_to_minutes(adapter['length'])
        
        #If the release date is known, convert it to a date format.
        if adapter["date"] != "TBR":
            adapter['date'] = self.convert_fr_date(adapter['date'])
        
        #Transorm comas into pipes |
        adapter["langage"] = adapter["langage"].replace(", ", "|")
        
        adapter["nationality"] = adapter["nationality"].replace(" ", "|")

        return item

    def close_spider(self, spider):
        """
        On the spider closing, create a parquet file from the created .csv
        """
        
        df = pd.read_csv("./allocine_spider.csv")
        df.to_parquet("allocine_spider.parquet", index=False)
    
    
    def hours_to_minutes(self, h)  -> int:
        """
        Transform string formatted movie length into minutes.
        """
        
        split = h.split()
        hours = split[0].split("h")[0]
        hours = int(hours)*60
        minutes = split[1].split("min")[0]
        
        return int(hours) + int(minutes)

    def convert_fr_date(self, date_str) -> datetime:

        """
        Convert a string formatted date into a datetime object.
        """
        
        for fr, en in self.mois_fr_to_en.items():
            date_str = date_str.replace(fr, en)
        
        return datetime.strptime(date_str, '%d %B %Y').date()