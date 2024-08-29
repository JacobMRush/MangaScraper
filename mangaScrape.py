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
mangakakalotBase = "https://https://mangakakalot.com"
headers = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

BASE_DLPATH = "D:/MANGA STORAGE"


def search_manga():
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
    selected_manga = input("Select a manga from the list: ")
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
            create_entry(selected_manga_title,
                         manga_results[int(selected_manga)-1].parent, manga_genre_tags, manga_results[int(
                             selected_manga)-1]['href'], mangaSeeBase)

        else:
            print("Item not added")
            return
    else:
        print("Please choose a correct index, the current index is out of range")


def manga_list_lookup(links, mangaSite):
    for link in links:
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        find_latest(soup, mangaSite)


def find_latest(soup, mangaSite):
    link = soup.find('a', class_="list-group-item")
    latestChapter = mangaSite + link['href'].replace("-page-1", "")
    print(latestChapter)
    rip_manga(latestChapter)


def create_entry(selectedTitle, selectedManga, manga_genre_tags, search_url, base_url):
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
                extraneous_char[j] = extraneous_char[j].replace(
                    '\n', '').replace('\t', '')
                cleanData.append(extraneous_char[j])
            continue
        else:
            cleanData.append(
                raw_manga_data[i].text.replace('\n', '').replace('\t', ''))
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


def insert_to_file(new_entry):
    # managed json file
    print(new_entry)
    with open('mangaData.json', "r") as outfile:
        data = json.load(outfile)
    data.append(new_entry)
    print(data)
    with open('mangaData.json', "w") as outfile:
        json.dump(data, outfile, indent=4)


def update_entry():
    print('a')
    # if data entry with manga name and link DNE, call create_entry
    # otherwise continue here
    # take information from find latest
    # update mangaData.json with latest chapter, metadata,


def download_manga():
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
    default_pages = 5
    for i in reversed(range(download_start_idx+1)):
        # verify that chapter_list[i] is NOT out of range
        if (0 <= i) and (i < len(chapter_list)):
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
            time.sleep(randint(20, 47))
        else:
            print("No more chapters to gather: Last updated at " +
                  data[manga_idx]['lastUpdated'])


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
    return True
# manga_list_lookup(mangaSee, mangaSeeBase)


# function to query our webpages (manga main pages with list of chapters) ------------ DONE
# what is the latest chapter       ---------------- DONE


# function that rips images from actual chapter page
# rip images from selected chapter page
# store images under "Chapter XX" folder
# function to update mangaData

def main():
    print("Hello, welcome and select your required operation")
    print("1. Search/Select Manga")
    print("2. Update MangaData")
    print("3. Download Manga")
    selection = input()

    match selection:
        case "1":
            search_manga()
        case "2":
            update_entry()
        case "3":
            download_manga()
        case _:
            print("Oops!")
    # update entry
    # used to update if manga is complete, chapter count, etc

    # delete entry
    # remove entry (drop a title) - or just add a "DROPPED" tag which ignores all other commands


main()
