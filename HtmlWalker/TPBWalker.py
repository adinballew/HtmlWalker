import urllib2
import re
from datetime import date
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
OUT_OF_RANGE = False


def read_url(url, order):
    page = 0
    global OUT_OF_RANGE
    OUT_OF_RANGE = False
    while not OUT_OF_RANGE:
        url_page = '{0}/{1}/{2}'.format(url, page, order)
        try:
            html_request = urllib2.Request(url_page, None, headers)  # Downloads html data
            html = urllib2.urlopen(html_request).read()
            print 'Getting HTML Data:', url_page
            if html is not None:
                soup = BeautifulSoup(html, 'html.parser')
                search_results = soup.find_all("table", {"id": "searchResult"})
                for result in search_results:
                    if order == 3:
                        font_tag = result.find_all("font")
                        last_result = font_tag[-1:][0].text.split()
                        last_date = last_result[1]
                        compare_date(last_date)
                        get_data(result)
                    else:
                        get_data(result)
        except urllib2.HTTPError as err:
            if err.code == 404:
                print 'Page Not found'
            else:
                print 'HTTPError!'
        page += 1


def compare_date(str_date):
    global OUT_OF_RANGE
    today = date.today()
    if "-" in str_date and "Y" not in str_date:
        split_date = re.split('[-]', str_date)
        upload_month = int(split_date[0])
        upload_day = int(split_date[1])
        upload_date = date(today.year, upload_month, upload_day)
        date_difference = (today - upload_date).days
        if date_difference >= 1:
            OUT_OF_RANGE = True


def get_desired():
    with open("DesiredShows.txt") as desired_shows:
        return desired_shows.read().splitlines()


def get_downloaded():
    with open("DownloadedShows.txt") as downloaded_shows:
        return downloaded_shows.read().splitlines()


def trim_magnet(magnet_link):
    show_name = re.search("&dn=(.*?)&", magnet_link).group(1)
    show_name = re.sub("x264-(.*)", "", show_name)
    show_name = re.sub("x264 - (.*)", "", show_name)
    show_name = re.sub("h264-(.*)", "", show_name)
    show_name = re.sub("H264-(.*)", "", show_name)
    show_name = re.sub("H.264-(.*)", "", show_name)
    show_name = show_name.replace(".", " ").rstrip()
    show_name = show_name.replace("+", " ").rstrip()
    return show_name


def filter_shows(magnet_link):
    show_name = trim_magnet(magnet_link)
    if "TS" not in show_name and "CAM" not in show_name and "Hindi" not in show_name:
        print show_name
    # desired = get_desired()
    # downloaded = get_downloaded()
    # for show in desired:
    #     if show in show_name and show not in downloaded:
    #         with open("DownloadedShows.txt", "w") as downloaded_shows:
    #             downloaded_shows.write(show_name)
    #             downloaded.append(show_name)
    #         os.startfile(magnet_link)
    #         print "Downloading", show_name


def get_data(result):
    try:
        table_rows = result.find_all("tr")
        for row in table_rows:
            anchor_tags = row.find_all("a")
            for info in anchor_tags:
                if info.find("img", {"title": "VIP"}) is not None:
                    for info2 in anchor_tags:
                        magnet_link = info2.get("href", None)
                        if magnet_link is not None and "magnet" in magnet_link:
                            filter_shows(magnet_link)
    except TypeError as err:
        print err


def user_search(urls):
    read_url(urls, 3)


def top_search(urls):
    print '1: Most Recent'
    print '2: Most Seeded'
    num = input('What Order show the results be in: ')
    options = {
        1: 3,
        2: 7
    }
    read_url(urls, options[num])


def main():
    while True:
        search_list = ('https://thepiratebay.org/user/ettv',
                       'https://thepiratebay.org/user/EtHD',
                       'https://thepiratebay.org/user/TvTeam',
                       'https://thepiratebay.org/browse/201',)
        print '1: ettv'
        print '2: EtHD'
        print '3: TvTeam'
        print '4: Top Shows'
        try:
            num = input('What Search would you like to run: ')
            options = {
                1: user_search,
                2: user_search,
                3: user_search,
                4: top_search
            }
            options[num](search_list[num - 1])
        except Exception as err:
            print "Error:", err


main()
