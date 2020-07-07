import requests
from bs4 import BeautifulSoup
import string
import argparse as parser
import os
from time import sleep

# TODO Add a sleep option to allow a specific amount of time between requests. Can be randomized

# Standard headers to prevent problems while scraping. May not all be necessary, they are
# copied from what my browser sent to the page.
headers = {
    'authority': 'prnt.sc',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'
}

# List of all possible characters in a prnt.sc code, base stores the length of this.
# The idea is that we can work in base 36 (length of all lowercase + digits) to add
# one to a code i.e. if we have abcdef, we can essentially write abcdef + 1 to get
# abcdeg, which is the next code.
code_chars = list(string.ascii_lowercase) + ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
base = len(code_chars)


# Converts digit to a letter based on character codes
def digit_to_char(digit):
    if digit < 10:
        return str(digit)
    return chr(ord('a') + digit - 10)


# Returns the string representation of a number in a given base.
# Credit: https://stackoverflow.com/a/2063535
def str_base(number, base):
    if number < 0:
        return '-' + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digit_to_char(m)
    return digit_to_char(m)


# Returns the next code given the current code
def next_code(curr_code):
    curr_code_num = int(curr_code, base)
    return str_base(curr_code_num + 1, base)


# Parses the HTML from the prnt.sc page to get the image URL.
def get_img_url(code):
    html = requests.get(f"http://prnt.sc/{code}", headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    img_url = soup.find_all('img', {'class': 'no-click screenshot-image'})
    return img_url[0]['src']


# Saves image from URL
def get_img(url, path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"{path}.png", 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':

    parser = parser.ArgumentParser()
    parser.add_argument('--start_code', help='6 character string made up of lowercase letters and numbers which is '
                                             'where the scraper will start. e.g. abcdef -> abcdeg -> abcdeh',
                        default='sahy60')
    parser.add_argument('--count', help='The number of images to scrape.', default='200')
    parser.add_argument('--output_path', help='The path where images will be stored.', default='output/')

    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    code = args.start_code
    for i in range(int(args.count)):
        code = next_code(code)
        try:
            url = get_img_url(code)
            get_img(url, args.output_path + f"/{code}")
            print(f"Saved image number {i + 1}/{args.count} with code: {code}")
        except:
            print(f"Error with image: {code}")
