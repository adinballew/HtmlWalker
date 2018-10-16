import urllib2
import os
import errno
import datetime
import socket
from multiprocessing.dummy import Pool as Threadpool
from bs4 import BeautifulSoup

parent_folder = "UserData"
retries = 0


def make_directory():
    """
    Makes Parent Directory to store Data
    :return:
    """
    try:
        if not os.path.exists(parent_folder):
            os.makedirs(parent_folder)
            print 'Making Directory:', os.getcwd() + ("\\{0}".format(parent_folder))
        else:
            print "Directory Exists:", os.getcwd() + ("\\{0}".format(parent_folder))
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise


def find_users(url):
    """
    Finds all Users
    :param url:
    :return links:
    """
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response, 'html.parser')
    desiredTag = soup.find_all('a')
    links = ()
    for tag in desiredTag:
        link = tag.get('href', None)
        if link is not None and "http://www.nsuok.edu/directory/profile" in link:
            links += link,
    print 'Done getting links'
    return links


def read_url(url):
    global retries
    while True:
        try:
            html_request = urllib2.Request(url)  # Downloads html data
            html = urllib2.urlopen(html_request).read()
            print url
            if html is not None:
                return html
        except urllib2.HTTPError as err:
            if err.code == 404:
                print 'Page Not found'
            else:
                print 'HTTPError!'
        except urllib2.URLError:
            print 'URLError!'
            retries += 1
            continue
        except socket.error, err:
            if err.errno == 10054:
                print 'Connection Closed!'
                retries += 1
                continue
            else:
                print err
        break


def retrieve_html(user_links, thread_count):
    global retries
    print "Downloading Urls:"
    start = datetime.datetime.now()
    results = mobilize_threads(user_links, thread_count, read_url)  # Mobilizes threads to visit Urls returns Map
    end = datetime.datetime.now()

    print 'Finished in:', ((end - start).total_seconds())  # Used to track total completion time
    print 'Urls Retried: ', retries  # Quantity of urls needing retries
    return results


def get_info(info_data):
    """
    <div class="content-half" id="profInfo">
        <h2> Some Full Name </h2>
        <p>
            <a href=... style=... title=...>userid@nsuok.edu</a>
        </p>
        <ul>
            <li><strong>Some Occupation</strong><br/>Some Department</li>
        </ul>
        <h3>Office Location</h3>
        <ul>
            <li><strong>City</strong></li>
            <ul>
                <li>Room Number</li>
                <li>Phone: (###) ###-####</li>
            </ul>
        </ul>
    </div>
    """
    user_data = {"fullname": None, "email": None, "info": []}
    try:
        for header2 in info_data.find_all("h2"):
            user_data["fullname"] = header2.text.lstrip().rstrip()

        for p in info_data.find_all("p"):
            for anchor in p.find_all("a"):
                user_data["email"] = anchor.text
        ulelements = info_data.find_all("ul", recursive=False)  # Stops recursive ul lookup

        if ulelements:  # Checks if list items exist
            for items in ulelements:
                for br in items.find_all("br"):
                    br.extract()
                for li in items.find_all("li"):
                    for strong in li.find_all("strong"):
                        user_data["info"].append(strong.text)
                        strong.extract()
                    if len(li.text) > 0:
                        user_data["info"].append(li.text)
    except IndexError:
        pass
    except TypeError as err:
        print err
    return user_data


def get_img_src(img_data):
    """
    <div class="content-half" id="profile">
        <img alt=" Some Full Name " src="/some/image/path.jpg"/>
    </div>
    """
    for img_tag in img_data.find_all("img"):
        src = img_tag.get("src")
        return src


def extract_data(results):
    """
    <div class="container" id="container-profile">
        <div class="content-half" id="profile">
            <img alt=" Some Full Name " src="/some/image/path.jpg"/>
        </div>
        <div class="content-half" id="profInfo">
            <h2> Some Full Name </h2>
            <p>
                <a href=... style=... title=...>userid@nsuok.edu</a>
            </p>
            <ul>
                <li><strong>Some Occupation</strong><br/>Some Department</li>
            </ul>
            <h3>Office Location</h3>
            <ul>
                <li><strong>City</strong></li>
                <ul>
                    <li>Room Number</li>
                    <li>Phone: (###) ###-####</li>
                </ul>
            </ul>
        </div>
    </div>
    """
    # TODO: Possibly Modify Code to build folders on extract
    user_info = None
    image_path = None
    user_data_list = []
    try:
        for html_data in results:
            soup = BeautifulSoup(html_data, 'html.parser')
            container = soup.find_all("div", {"id": "container-profile"})  # Finds Profile Container
            for subcontainer in container:
                profile_img = subcontainer.find_all("div", {"id": "profile"})  # Finds Profile Image Container
                profile_info = subcontainer.find_all("div", {"id": "profInfo"})  # Finds Profile Info Container
                for info_data in profile_info:
                    user_info = get_info(info_data)  # Get User Info
                for img_data in profile_img:
                    image_path = get_img_src(img_data)  # Get User Image
            user_data_list.append((user_info, image_path,))
    except TypeError as err:
        print err
    return user_data_list


def make_child_directory(child_directory):
    try:
        if not os.path.exists(parent_folder + "/{0}".format(child_directory)):
            os.makedirs(parent_folder + "/{0}".format(child_directory))
            print 'Making Directory:', ("{0}\\{1}\\{2}".format(os.getcwd(), parent_folder, child_directory))
        else:
            print "Directory Exists:", ("{0}\\{1}\\{2}".format(os.getcwd(), parent_folder, child_directory))
    except OSError as err:
        if err.errno != errno.EEXIST:
            raise


def get_image(img_url):
    while True:  # Until we get image data
        try:
            img_request = urllib2.Request(img_url)  # Downloads Image
            img_data = urllib2.urlopen(img_request).read()
            return img_data
        except urllib2.URLError:
            print 'URLError!'
            continue
        except socket.error, err:
            if err.errno == 10054:
                print 'Connection Closed!'
                continue
            else:
                print err
        break


def populate_portfolio(folder_name, img_filename, img_data, info, email):
    user_img = open("./{0}/{1}/{2}".format(parent_folder, folder_name, img_filename), "wb")
    user_img.write(img_data)
    user_img.close()

    user_file = open("./{0}/{1}/{1}.txt".format(parent_folder, folder_name), "wb")
    user_file.writelines(email + "\n")
    for data in info:
        if data is not None:
            user_file.writelines(data + "\n")
        else:
            user_file.writelines("Not Available")
    user_file.close()


def build_portfolio(user_data):
    profile = user_data[0]
    image_path = user_data[1]
    email = profile.get("email")
    info = profile.get("info")
    img_url = "http://www.nsuok.edu{0}".format(image_path)  # Appends image path to parent url for path
    img_filename = os.path.basename(image_path)  # Gets base image name
    folder_name = profile.get("fullname").replace(" ", "_")  # Replaces spaces with underscores

    make_child_directory(folder_name)  # Makes folder with username as name
    img_data = get_image(img_url)
    populate_portfolio(folder_name, img_filename, img_data, info, email)


def create_user_profile(user_data_list, thread_count):
    print "Building Portfolios"
    mobilize_threads(user_data_list, thread_count, build_portfolio)  # Mobilizes thread to build user portfolio


def mobilize_threads(items, thread_count, function):
    """
    Maps function to some iterable
    :param items:
    :param thread_count:
    :param function:
    :return results:
    """
    pool = Threadpool(thread_count)
    results = pool.map(function, items)  # Maps function to each Url
    pool.close()  # Closes Pool
    pool.join()  # Joins pool back to synchronous

    return results


def main():
    url = "https://www.nsuok.edu/directory/AllUsers.aspx"  # Base Url
    thread_count = 8  # Number of threads to Mobilize
    make_directory()

    # user_links = ("http://www.nsuok.edu/directory/profile/adairja.aspx",
    #               "http://www.nsuok.edu/directory/profile/brockm.aspx",
    #               "http://www.nsuok.edu/directory/profile/asbill01.aspx",
    #               "http://www.nsuok.edu/directory/profile/adairsmi.aspx",)
    user_links = find_users(url)
    results = retrieve_html(user_links, thread_count)
    user_data_list = extract_data(results)
    create_user_profile(user_data_list, thread_count)


main()
