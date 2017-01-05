"""
The code resumes if files have been already created for certain counties , hence you can stop in the middle and then
you can resume.
"""
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from pathlib import Path
import csv
import os

def generalized_table_scrapper(url,href_col,col_no):
    """
    This is a web scrapper that scrapes html tables found a webpage this is specifically writen to extract data
    from a html table that contains counties of England and their respective postal codes.

    :param          url             : The website containing the table
    :param          href_col        : Column containing the next hop link in our html table
    :param          col_no          : The no of columns present in our table to extract data from

    :return         :  Nothing
    """
    # This is a technique of creating a user agent when websites contain spider bots to prevent automated scraping
    #we fool it to think that it is a instance of a browser that is trying to access the webpage.

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }

    request = Request(url, None, headers)  # The assembled request
    response = urlopen(request)
    data = response.read()  # The data u need

    # Now we process the raw html to get our tabular data
    soup = BeautifulSoup(data, "lxml")
    tables = soup.find_all('table')
    # print("Tables are of type --> " + str(type(tables)))
    table_body = tables[0].find('tbody')
    # print(table_body)

    rows_tables = table_body.find_all("tr")

    data = []
    links = []

    for row in rows_tables:
        col = row.find_all("td")
        data_col = [elem.text.strip() for elem in col]
        dummy_col = [elem for elem in col]
        if (len(data_col) == col_no and data_col != ''):
            towns_link = ""
            if (dummy_col[href_col].find('a') != None):
                towns_link = dummy_col[href_col].find('a').get('href')
            data.append(data_col)
            links.append(towns_link)

    return data, links


def get_postal_code(url):
    """
    This method follows the link scraped from the main county tables and check for the postal code for a
    given county on an html table

    :param          url : The webpage meant to crawl for the postal code

    :return         : Nothing
    """
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = Request(url, None, headers)  # The assembled request
    response = urlopen(request)
    data = response.read()

    soup = BeautifulSoup(data, "lxml")
    tables = soup.find_all('table')
    table_body = tables[0].find('tbody')

    rows_tables = table_body.find_all("tr")
    if len(rows_tables) > 2:
        col = rows_tables[2].find_all("td")
        data_col = [elem.text.strip() for elem in col]
        result = data_col[1]
    else:
        result = ""

    return result


def city_county_postcode_mapper(url):
    """
    This function calls the generalized_table_scrapper to scrape the html tables from the websites and then create
    the overall mapping needed from crawling this webspace, we write a .csv file for every county into the County_files
    folder

    :param          url     : The the website to scrape

    :return:        Nothing
    """
    print("\n*******************--- Starting Web Scrapper for County Data of England ---*******************")
    print("\n")

    # County_data --> index,county,towns_link,country,no_of_towns
    county_data, town_links = generalized_table_scrapper(url+"/towns-in-uk/",2,5)

    if os.path.exists("County_Files"+os.path.sep) == False:
        os.makedirs("County_Files"+os.path.sep)

    for link in range(len(town_links)):

        my_file = Path("County_Files"+os.path.sep+county_data[link][1]+".csv")

        if my_file.is_file():
            continue

        else:
            with open("County_Files"+os.path.sep+county_data[link][1]+".csv","w+") as wp:
                writer = csv.writer(wp)
                new_url = url + town_links[link]
                towns_in_county, postcode_links = generalized_table_scrapper(new_url,1,3)
                check = 0
                for town in range(len(postcode_links)):
                    postal_code = ""
                    if(len(postcode_links[town])>1):
                        postal_code = get_postal_code(url+postcode_links[town])
                    row =[towns_in_county[town][1],postal_code]
                    if len(county_data[link])>=5:
                        row.append(county_data[link][1])
                        row.append(county_data[link][3])
                    writer.writerow(row)
                    check+=1
                print("\nFinished Writing --> " + "County_Files"+os.path.sep+county_data[link][1]+".csv")
                print("Writtern --> " + str(check) + " rows")
                wp.close()

    print("\n*******************--- Finished Scrapping County Data ---*******************")



def county_file_merger(folder_path):
    """
    This method reads all files containing county data in the given folder and it  merges all the different county data's
    into one .csv file for easier review.

    :param          folder_path : The path to the folder containing all the county file's that contain data

    :return         Nothing
    """

    print("\n*******************--- Starting File Merger for .csv files ---*******************")
    with open("result.csv","wb") as outfile:
        for filename in os.listdir(folder_path):
            with open(filename,"rb") as infile:
                for line in infile:
                    outfile.write(line)
            infile.close()
    outfile.close()
    print("\nResult saved to -----> result.csv ")
    print("\n*******************--- Finished File Merger for .csv files ---*******************")


def main():
    """

    :return:
    """
    print("\n############################################## STARTING COUNTY WEB SCRAPER ##############################################")
    # print("\n")
    city_county_postcode_mapper("https://www.townscountiespostcodes.co.uk")
    county_file_merger("County_Files")
    print("\n")
    print("\n############################################## FINISHED COUNTY WEB SCRAPER ##############################################")


if __name__ == main():
    main()