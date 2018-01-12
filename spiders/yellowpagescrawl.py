# -*- coding: utf-8 -*-
# State the import
import scrapy
import base64
import sys
from termcolor import colored # import the red color in terminal
from YellowPages.items import YellowpagesItem

# CREATE THE SPIDER
class YellowpagescrawlSpider(scrapy.Spider):
    name="myspider"

    allowed_domains = ["www.pagesjaunes.fr", "www.pagesjaunes.com"]

    def start_requests(self):

        # Function to visit the first page
        url = 'https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui={}&ou={}&page={}'

        try:
            if(self.source and self.source and self.entity and self.area):
                print("All fields are field properly!")
                page=0
                yield scrapy.Request(url.format(str(self.entity), str(self.area), page),callback=self.parse_totalpages, meta={"source": str(self.source), "entity": str(self.entity), "area": str(self.area)})
        except AttributeError:
            colorred = "\033[01;31m{0}\033[00m"
            print(colorred.format("Warning!. Set the proper arguments in order to start: -a source='' -a entity='' -a area=''  (example: scrapy crawl myspider -a entity='macons'area='Bordeaux') "))

    def parse_totalpages(self, response):
        # Function to get the total number of pages

        source = response.meta.get("source")
        entity = response.meta.get("entity")
        area = response.meta.get("area")

        url = 'https://www.pagesjaunes.fr/annuaire/chercherlespros?quoiqui={}&ou={}&page={}'
        self.logger.info("%s page visited", response.url)
        total_pages = response.css('.pagination-compteur::text').extract_first()
        print ("total_pages are %s" %total_pages)

        if(total_pages):
            print(total_pages)
            get_pages = total_pages.split() # split the string into a list
            print(get_pages)
            get_pages = get_pages[1]
            if get_pages.isdigit():
                for page in range(int(get_pages) + 1):
                    # Make a loop request for each page identified
                    yield scrapy.Request(url.format(entity, area, page), callback=self.parse, meta={"source": source})

    def parse(self, response):
        # Function that goes to each page and extract data from each article from those 20 of them
        self.logger.info("%s page visited", response.url)

        print('Get the articles links from >>>', response.url)
        source = response.meta.get("source")
        number_of_results = response.css(".denombrement ::text").extract_first()
        elements=[]
        count = 0
        try:
            code_rubrique = response.css(".head-main-content  img::attr(src)").extract()[-1]
            code_rubrique = code_rubrique.split("_")
            code_rubrique = code_rubrique[1]
            code_rubrique = code_rubrique.split("&")
            code_rubrique = code_rubrique[0]

        except IndexError:
            colorred = "\033[01;31m{0}\033[00m"
            print(colorred.format("Could not retrive the code_rubrique variable"))

        for item in response.css('article'):

            count +=1
            link = item.css("a.denomination-links ::attr(href)").extract_first()
            tel = item.css('.bi-contact-tel strong ::text').extract_first().strip()
            email = item.css(".hidden-phone.SEL-email  ::attr(data-pjlb)").extract_first()
            if email:
                email = email.split(":")
                email = email[1]
                email = email.split('"')
                email = email[1]
                email = str(base64.b64decode(email))
                email = email.split("'")
                email = email[1]
                email = 'https://www.pagesjaunes.fr' + email

            website = item.css(".item.hidden-phone.site-internet.SEL-internet a::attr(href)").extract_first()

            if(str(link) != "#"):
                url = 'https://www.pagesjaunes.fr' + str(link)
                yield scrapy.Request(url, callback=self.get_content, meta={"email_url": email, "telephone": tel, "number_of_results": number_of_results, "website": website, "source": source})
            elif(str(link) == "#"):
                elements.append(count)
                link = item.css(".bi-bloc ::attr(data-pjtoggleclasshisto)").extract_first()
                link=link.split(":")
                bloc_id = link[2].split(" ")
                bloc_id = bloc_id[1]
                bloc_id = bloc_id.split('"')
                bloc_id = bloc_id[1]
                no_sequence = link[3].split(" ")
                no_sequence = no_sequence[1]
                no_sequence = no_sequence.split('"')
                no_sequence = no_sequence[1]
                url = "https://www.pagesjaunes.fr/pros/detail?bloc_id={bloc_id}&no_sequence={no_sequence}&code_rubrique={code_rubrique}". format(bloc_id=bloc_id, no_sequence=no_sequence, code_rubrique=code_rubrique)
                yield scrapy.Request(url, callback=self.get_content, meta={"email_url": email, "telephone": tel, "number_of_results": number_of_results, "website": website, "source": source })

        print("Total Number of Articles are: ", count)
        print("The articles number without a href: ", elements)

    def get_content(self, response):
        # Function that access each article and extracts further the data required

        self.logger.info("%s page visited", response.url)
        print('parse url >>>', response.url)

        email_url = response.meta.get("email_url")
        number_of_results = response.meta.get("number_of_results")
        website = response.meta.get("website")
        source = response.meta.get("source")
        # Get the item from items.py
        json_dict = YellowpagesItem()
        telephone = response.meta.get("telephone")
        title = response.css('.noTrad ::text').extract_first().strip()
        print("Number of search results", number_of_results)
        print(title)
        json_dict["source"] = source
        json_dict["title"] = title

        # Extract the adress
        adre0 = response.css("span[class=noTrad] ::text").extract()[0].strip()
        adre1 = response.css("span[class=noTrad] ::text").extract()[1].strip()
        adre2 = response.css("span[class=noTrad] ::text").extract()[2].strip()

        adress = adre0 + " " + adre1 + adre2
        print(adress)
        json_dict["adress"] = adress
        # Extract the image logo for each company
        logo = response.css(".logo-cviv img ::attr(src)").extract_first()
        if logo is not None:
            logo = "https:" + str(logo)
            json_dict["logo"] = logo
        else:
            json_dict["logo"] = "No logo found"
        if email_url is not None:
            json_dict["email"] = email_url
        else:
            json_dict["email"] = "No email url found"

        if telephone is not None:
            json_dict["phone"] = telephone
        else:
            json_dict["phone"] = "No phone number found"

        if website is not None:
            if website !="#":
                json_dict["website"] = website
            else:
                json_dict["website"] = "No website found"
        else:
            json_dict["website"] = "No website found"
        # Keep the items for further storange into .json format
        yield json_dict
