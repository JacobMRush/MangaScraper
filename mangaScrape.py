import json
import pathlib
import requests
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import time
from random import randint

options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=options)
mangaSeeBase = "https://mangasee123.com"
mangakakalotBase = "https://mangakakalot.com"
headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.3"

BASE_DLPATH = "D:/MANGA STORAGE"


def clean_and_strip(item):
    item = item.replace('\n', "").replace('\t', "").strip()
    return item


def search_manga_ms():
    user_manga = input("Enter manga: ")
    search_url = "https://mangasee123.com/search/?name=" + user_manga
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_dne = soup.find('div', class_="NoResults")
    if manga_dne:
        print("Please enter a valid manga name, " + user_manga + " not found")
        return -1
    # continue and show user list of manga names and links
    manga_results = soup.find_all('a', class_="SeriesName ng-binding")
    # now we have a list of manga results
    # take these and their names and display them to the user, ask the user to select one, and ask if the user would like to add that manga
    # to their list
    for i in range(len(manga_results)):
        list_num = i+1
        print(str(list_num) + ". " + manga_results[i].text)
    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_results):
        print("You have selected " +
              manga_results[int(selected_manga)-1].text + "! ")
        answer = input(
            "Would you like to add this manga to your library? Y/N: ")
        if answer == "Y" or answer == "y":
            print("yes")
            selected_manga_title = manga_results[int(selected_manga)-1].text
            print(selected_manga_title)
            print("--------------------")
            # send title and genre seperately than the rest of raw data
            manga_genre_tags = manga_results[int(
                selected_manga)-1].parent.findAll('span', "ng-binding ng-scope")
            create_entry_ms(selected_manga_title,
                            manga_results[int(selected_manga)-1].parent, manga_genre_tags, manga_results[int(
                                selected_manga)-1]['href'], mangaSeeBase)

        else:
            print("Item not added")
            return
    else:
        print("Please choose a correct index, the current index is out of range")


def search_manga_mk():
    user_manga = input("Enter manga: ")
    # seperate by inserting base url at the first index before adding any data, will check for domain change, and will label as such to user
    search_url = "https://mangakakalot.com/search/story/" + user_manga
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_data_list = soup.findAll('div', class_="story_item")
    if (manga_data_list == []):
        print("Nothing found on mangakakalot, please retry your search or select from another source")
        return
    # process data and then create a entry in mangadata.json
    for i in range(len(manga_data_list)):
        title = manga_data_list[i].find('h3', class_="story_name").text
        title = clean_and_strip(title)
        list_num = i+1
        print(str(list_num) + ". " + title)
    selected_manga = input("Select a manga from the given list: ")
    if 0 <= int(selected_manga)-1 <= len(manga_data_list):
        title = manga_data_list[int(
            selected_manga)-1].find('h3', class_="story_name")
        story_link = title.find('a')['href']
        title = clean_and_strip(title.text)
        print("You have selected " + title + "! ")
        print(manga_data_list[int(selected_manga)-1])
        story_item_right = manga_data_list[int(
            selected_manga)-1].find('div', class_="story_item_right")
        story_latest_chapter = story_item_right.find(
            'em', class_="story_chapter").text
        story_latest_chapter = clean_and_strip(story_latest_chapter)
        story_data = story_item_right.findAll("span")
        story_author = clean_and_strip(story_data[0].text.split(':')[1])
        story_last_updated = clean_and_strip(story_data[1].text.split(':')[1])
        # print(title)
        # print(story_latest_chapter)
        # print(story_author)
        # print(story_last_updated)
        # print(mangakakalotBase)
        # print(story_link)
        genres, status = get_genre_status(story_link)
        # title, latest chapter, author, last updated, source, link, status genre nato, need more work done to do it on main domain
        # N/A: released, translation, type
    else:
        print("Please select a valid item from the list")
        return


def get_genre_status(link):
    status = -1
    genre_list = []
    driver.get(link)
    domain = link.split("/manga")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print(domain[0])
    # multiple domains that the manga redirects to
    if (domain[0] == "https://mangakakalot.com"):
        container = soup.find("ul", class_="manga-info-text")
    if (domain[0] == "https://chapmanganato.to"):
        container = soup.find("table", class_="variations-tableInfo")
        container = container.findAll('tr')
        for i in range(len(container)):
            # find first table data in each row with the tag "status and genres"
            td = container[i].find('td')
            td_desc = clean_and_strip(td.text)
            if (td_desc == 'Status :'):
                status = container[i].findAll('td')
                status = clean_and_strip(status[1].text)
            elif (td_desc == 'Genres :'):
                genre_group = container[i].findAll('td')
                genre_group = genre_group[1].findAll('a')
                for item in range(len(genre_group)):
                    genre_list.append(genre_group[item].text)
    return genre_list, status


def mk_nato_page(link):
    print('a')


def mk_main_page(link):
    print('a')


def create_entry_ms(selectedTitle, selectedManga, manga_genre_tags, search_url, base_url):
    # check if selected title is saved in file, if not go for it!
    raw_manga_data = selectedManga.findAll('div', "ng-scope")
    cleanData = []
    clean_genre_list = []
    # loop through this array and get text for author, year, status, latest chapter (and date updated) and genres (AND LINK)
    for i in range(len(raw_manga_data)):
        # want to seperate year and author, splitting gives a list of size 2, inserting these back
        if '·' in raw_manga_data[i].text:
            extraneous_char = raw_manga_data[i].text.split('·')
            for j in range(len(extraneous_char)):
                extraneous_char[j] = clean_and_strip(extraneous_char[j])
                cleanData.append(extraneous_char[j])
            continue
        else:
            cleanData.append(clean_and_strip(raw_manga_data[i].text))
    cleanData.append(selectedTitle)
    for i in range(len(manga_genre_tags)):
        # strip of leading and trailing spaces,
        clean_genre_list.append(
            manga_genre_tags[i].text.strip('\n\t, '))
    # turn this processed list into a json object to store in my list of manga the user wants to keep updated or is interested in
    clean_genre_list.pop(0)
    # remove everything prior and including :
    for i in range(len(cleanData)):
        if (':' in cleanData[i]):
            split = cleanData[i].split(':')
            split[1] = split[1].strip(' ')
            cleanData[i] = split[1]
        else:
            continue
    cleanData[3] = cleanData[3].split(" ")[1]
    new_entry = {
        "author": cleanData[0],
        "released": cleanData[1],
        "status": cleanData[2],
        "lastChapter": cleanData[3],
        "lastUpdated": cleanData[4],
        "translation": cleanData[5],
        "title": selectedTitle,
        "genres": clean_genre_list,
        "type": "",
        "link": base_url + search_url,
        "source": base_url,
        "lastRipped": -1
    }
    insert_to_file(new_entry)

# STAYS THE SAME ON UPDATE


def insert_to_file(new_entry):
    # managed json file
    print(new_entry)
    with open('mangaData.json', "r") as outfile:
        data = json.load(outfile)
    data.append(new_entry)
    print(data)
    with open('mangaData.json', "w") as outfile:
        json.dump(data, outfile, indent=4)

# WIP


def update_entry():
    type_info = -1
    status_info = -1
    full_status = -1
    data = view_manga()
    selected_manga = input("Select a entry to update: ")
    selected_manga = int(selected_manga) - 1
    print("You've chosen to update: " + data[selected_manga]['title'])
    driver.get(data[selected_manga]['link'])
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    manga_page = soup.findAll("li", class_="list-group-item d-none d-md-block")
    for item in manga_page:
        item_header = item.find('span', class_="mlabel").text
        if (item_header == "Status:"):
            status_info = item.findAll('a').text
        elif (item_header == "Type:"):
            type_info = item.find('a').text
    if (status_info == "" or status_info == [] or status_info == None):
        print("No status info found")
        status_info = -1
    if (type_info == "" or type_info == None):
        print("No Type found")
        type_info = -1
    # select latest chapter, get chapter number and date it was posted
    if (type_info != -1):
        data[selected_manga]['type'] = type_info
    if (len(status_info) == 1):
        full_status = status_info[0]
    elif (len(status_info) == 2):
        full_status = status_info[0] + ', ' + status_info[1]
    print(full_status)


def download_manga_mk():
    print('a')
# MANGASEE

# our "find manga" portion needs to verify that the selected manga is for mangasee


def download_manga_ms():
    found_list_idx = []
    # figure out which entry we want to rip from
    # pass pages with some debounce timer or something inbetween each scrape
    selected = input("Hello! Select a manga from your list to scrape: ")
    with open("mangaData.json", "r") as outfile:
        data = json.load(outfile)
    for i in range(len(data)):
        if (selected in data[i]['title'] or selected.capitalize() in data[i]["title"]):
            found_list_idx.append(i)
    if (len(found_list_idx) != 0):
        for i in range(len(found_list_idx)):
            print(str(i+1) + ": " + data[found_list_idx[i]]["title"])
        selected_manga_idx = input("Select a manga from your searched items: ")
        realIdx = found_list_idx[int(selected_manga_idx)-1]
        get_chapter_list(realIdx)

# MANGASEE HELPER


def get_chapter_list(manga_idx):
    chapter_list = []
    with open("mangaData.json", "r") as f:
        data = json.load(f)
    driver.get(data[manga_idx]["link"])
    expand_button = driver.find_element(By.CLASS_NAME, 'ShowAllChapters')
    expand_button.click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    anchor_tags = soup.find_all(
        'a', class_="list-group-item ChapterLink ng-scope")
    for i in range(len(anchor_tags)):
        chapter_list.append(anchor_tags[i]['href'].replace("-page-1", ""))
    download_handler(chapter_list, manga_idx)

# MANGASEE HELPER


def download_handler(chapter_list, manga_idx):
    # print(chapter_list, manga_idx)
    download_start_idx = -1
    with open("mangaData.json", "r") as f:
        data = json.load(f)
    if data[manga_idx]['lastRipped'] == -1:
        download_start_idx = len(chapter_list)-1
    else:
        # find the "lastRipped" chapter suffix in chapter_list array
        for i in range(len(chapter_list)):
            if data[manga_idx]['lastRipped'] == chapter_list[i]:
                download_start_idx = i-1
                break
    # update lastRipped each time I get a sucesss from rip_manga()
    print("Starting from: " + str(download_start_idx) +
          " at chapter " + chapter_list[download_start_idx])
    # we want to check if there exists x amount of pages:
    default_pages = 10
    if (download_start_idx < 0):
        print("No more chapters to gather: Last updated at " +
              data[manga_idx]['lastUpdated'] + " with chapter " + data[manga_idx]["lastChapter"])
        return
    for i in reversed(range(download_start_idx+1)):
        # verify that chapter_list[i] is NOT out of range
        print(chapter_list[i] + " WE ARE HERE " +
              str(default_pages) + " pages left")
        if (default_pages == 0):
            break
        if rip_manga(data[manga_idx]['source'] + chapter_list[i], data, manga_idx) != True:
            break
        else:
            print("Update the data with the latest lastRipped")
            data[manga_idx]['lastRipped'] = chapter_list[i]
            with open('mangaData.json', "w") as outfile:
                json.dump(data, outfile, indent=4)
        default_pages = default_pages-1
        time.sleep(randint(29, 62))
        if (0 >= i-1) and (i-1 > len(chapter_list)):
            print("No more chapters to gather: Last updated at " +
                  data[manga_idx]['lastUpdated'])
            break

# MANGASEE IMAGE SCRAPER


def rip_manga(page, data, manga_idx):
    driver.get(page)
    chapter_images = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    chapter_folder = soup.select_one(
        'button[data-target="#ChapterModal"]').text
    chapter_folder = chapter_folder.strip('\n\t ')
    if '-' not in chapter_folder:
        chapter_folder = 'S0 - ' + chapter_folder
    image_elements = soup.find_all('img', class_="img-fluid")
    # MANGA FOLDER / TITLE FOLDER / CHAPTER FOLDER
    # Chapter information can be taken from the target data chapter button
    try:
        pathlib.Path(BASE_DLPATH + "/" + data[manga_idx]['title'] +
                     "/" + chapter_folder).mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        return False
    # make request for each image src :)
    image_count = 0
    for img in image_elements:
        img_src = img.get('src')
        chapter_images.append(img_src)
    for image_url in chapter_images:
        fileName = image_url.split('/')
        fileName = fileName[len(fileName)-1]
        response = requests.get(image_url, headers={
                                'UserAgent': headers, 'referer': "https://mangasee123.com/"})
        if (response.status_code != 200):
            print("Error getting the current file")
            return False
        else:
            with open(BASE_DLPATH + "/" + data[manga_idx]['title'] +
                      "/" + chapter_folder + '/' + fileName, 'wb') as f:
                noop = f.write(response.content)
                print("Saved {}".format(BASE_DLPATH + "/" + data[manga_idx]['title'] +
                      "/" + chapter_folder + '/' + fileName))
        image_count += 1
        if image_count % 10 == 0:
            time.sleep(randint(9, 15))
    return True

# MANGAKAKALOT SCRAPER


def scrape_mangakakalot(page):
    chapter_images = []
    search_url = "https://chapmanganato.to/manga-aa951883/chapter-613"
    driver.get(search_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    image_container = soup.find('div', class_="container-chapter-reader")
    all_images = image_container.findAll('img')
    for img in all_images:
        if (img.has_attr('title')):
            img_src = img.get('src')
            chapter_images.append(img_src)
    print(chapter_images)
    for image_url in chapter_images:
        response = requests.get(image_url, headers={
                                'UserAgent': headers, 'referer': "https://chapmanganato.to/"})
        if (response.status_code != 200):
            print("Error getting the current file")
            return False
        else:
            print("Woooo we have our images")

# STAYS THE SAME


def view_manga():
    with open("mangaData.json", "r") as f:
        data = json.load(f)
    item_number = 0
    for item in range(len(data)):
        item_number += 1
        print(str(item_number) + ": " +
              data[item]['title'] + " at index " + str(item_number-1))
    return data


def view_manga_data():
    data = view_manga()
    selected_manga = input("Select a manga to get more details: ")
    selected_manga = int(selected_manga) - 1
    print("Here is some information on the manga you selected: ")
    print("-------------------------------")
    print(data[selected_manga]['title'])
    print(data[selected_manga]['status'])
    print(data[selected_manga]['lastUpdated'])
    print(data[selected_manga]['lastChapter'])
    print(data[selected_manga]['lastRipped'])
    print("-------------------------------")


def main():
    print("Hello, welcome and select your required operation")
    print("1. View manga list")
    print("2. Search/Select Manga - Mangasee")
    print("3. Search/Select Manga - Mangakakalot")
    print("4. Update Manga data")
    print("5. Download Manga - Mangasee")
    print("6. Download Manga - Mangakakalot")

    selection = input()

    match selection:
        case "1":
            view_manga_data()
        case "2":
            search_manga_ms()
        case "3":
            search_manga_mk()
        case "4":
            update_entry()
        case "5":
            download_manga_ms()
        case "6":
            download_manga_mk()
        case _:
            print("Oops!")


main()
