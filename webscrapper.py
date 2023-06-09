# Jonathan Ho
# CS 4395

'''This program crawls through a starting website to find other links relevant to a specific term.
It will then make files for each unique URL, clean up the text, and print out the 25 most used words.
Based off this, I created a list of 10 significant terms used to create a simple dictionary knowledge base'''

import os.path
import re
import urllib.request
import requests
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# Function to build the knowledge base
def build_kb(sig_terms):
    # Create dictionary with empty list
    built_base = {x: [] for x in sig_terms}

    file_num = 1
    doc_name = "URL " + str(file_num) + ".txt"

    # Append the sentence to its respective significant term
    while os.path.isfile(doc_name):
        with open(doc_name, 'r', encoding='utf-8') as f:
            sent = f.readlines()
            for line in sent:
                for word in sig_terms:
                    if word in line:
                        built_base[word].append(line)

        file_num += 1
        doc_name = "URL " + str(file_num) + ".txt"

    return built_base

# Private function to get the significant terms
def _get_sig_terms(file):
    sw_list = stopwords.words('english')
    tf_dict = {}
    tok = word_tokenize(file)
    tok = [x.lower() for x in tok if x.isalpha() and x not in sw_list]

    for t in tok:
        if t in tf_dict:
            tf_dict[t] += 1
        else:
            tf_dict[t] = 1

    for token in tf_dict.keys():
        tf_dict[token] = tf_dict[token] / len(tok)

    return tf_dict

# Find and print out important terms of each file
def print_file_terms():
    file_num = 1
    doc_name = "URL " + str(file_num) + ".txt"

    while os.path.isfile(doc_name):
        print("")
        print(doc_name + " important terms:")
        with open(doc_name, 'r', encoding='utf-8') as f:
            term_freq = _get_sig_terms(f.read())
            term_freq = sorted(term_freq.items(), key=lambda x: x[1], reverse=True)
            print(term_freq[:25])

        file_num += 1
        doc_name = "URL " + str(file_num) + ".txt"

# Writes sentences of each url into its respective file
def scrape_url():
    num = 1

    # Replaces any escape sequences
    def replace_esc_seq(url_text):
        # Takes out any escape sequences in the beginning or end of string

        #for line in url_text:
            
        #    print("This is the line:", line)
        #    line = re.sub(r'[/+=&.?!,:;()©\“”’\'\-\d]', '', line)

        #with open('log.txt', 'a', encoding='utf-8') as f:
        #    for url in url_text:
        #       f.write(url + '\n')
        new_list = [x.strip() for x in url_text]

        # Remove empty strings from list
        while '' in new_list:
            new_list.remove('')

        # Replace newlines and tabs
        new_list = [x.replace('\n', '') for x in new_list]
        new_list = [x.replace('\t', '') for x in new_list]

        for index, line in enumerate(new_list):
            new_list[index] = re.sub(r'[\>\<\[\]|\-\_\\\/\+\=&\?!\(\),:;©`\“\”\’\'\-\d]', '', line)

        return new_list
        #return url_text

    file_name = "URL " + str(num) + ".txt"

    # Goes through each file that contains the name "URL"
    while os.path.isfile(file_name):
        with open(file_name, 'r', encoding='utf-8') as fl:
            raw_lines = fl.readlines()
            new_lines = replace_esc_seq(raw_lines)  # apply function
            text = ' '.join(new_lines)
            sentence = sent_tokenize(text)

        with open(file_name, 'w', encoding='utf-8') as new_file:
            for sent in sentence:
                # New line for each sentence in file
                new_file.write(sent + '\n')

        num += 1
        file_name = "URL " + str(num) + ".txt"

# Function to get the text within links
def get_url_text():
    num = 1

    with open('unique_urls.txt', 'r') as uu:
        urls = uu.readlines()

        for link in urls:
            url_link = link

            def visible(element):
                if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                    return False
                elif re.match('<!--.*-->', str(element.encode('utf-8'))):
                    return False
                return True

            # Tries to open url, otherwise gives up and goes to next url
            try:
                html = urllib.request.urlopen(url_link, timeout=15)
                soup = BeautifulSoup(html, features="html.parser")
                data = soup.findAll(string=True)
                result = filter(visible, data)
                temp_list = list(result)
                temp_str = ' '.join(temp_list)
                file_name = 'URL ' + str(num) + '.txt'
                print("File " + str(num) + " done.")
                num += 1

                with open(file_name, 'w', encoding="utf-8") as f:
                    f.write(temp_str)

            except:
                print("ERROR: reading timed out leaving unfinished text")
                continue

# Function to remove any duplicate links
def remove_dupes():
    url_list = []

    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()
    for u in urls:
        url_list.append(u)

    # List comprehension to remove any duplicate links
    new_list = []
    [new_list.append(x) for x in url_list if x not in new_list]

    # Create new txt file with no dupes
    with open('unique_urls.txt', 'w') as nf:
        for link in new_list:
            nf.write(str(link) + '\n')

# Function to webcrawl given a link
def web_crawler(link):
    r = requests.get(link)

    data = r.text
    soup = BeautifulSoup(data, features="html.parser")

    # Writes urls to a urls.txt file
    with open('urls.txt', 'w') as f:
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            if 'Recipe' in link_str or 'recipe' in link_str:
                if link_str.startswith('/url?q='):
                    link_str = link_str[7:]
                if '&' in link_str:
                    i = link_str.find('&')
                    link_str = link_str[:i]
                if link_str.startswith('http') and 'google' not in link_str:
                    f.write(link_str + '\n')

if __name__ == '__main__':
    link_to_crawl = "https://www.google.com/search?q=recipe&sxsrf=APwXEdcDmMo3SWbYW8v0aiOiORGWqkpsoQ%3A1681266908574&ei=3Bg2ZLSwIpK5qtsPjKmG2Ao&oq=recipie&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQAxgCMgQIIxAnMgoIABCABBAUEIcCMgcIABCABBAKMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDIFCAAQgAQyBQgAEIAEMgUIABCABDoKCAAQRxDWBBCwAzoKCAAQigUQsAMQQzoICAAQigUQkQI6EAgAEIAEEBQQhwIQsQMQgwE6CAgAEIAEELEDSgQIQRgAUMUDWKQFYIcfaAFwAXgAgAFTiAGZAZIBATKYAQCgAQHIAQrAAQE&sclient=gws-wiz-serp"

    # Functions to web crawl, create files, and print out term frequencies of each file
    web_crawler(link_to_crawl)
    remove_dupes()
    get_url_text()
    scrape_url()
    print_file_terms()

    # 10 important terms from all files
    sig_terms = ['mario', 'nintendo', 'game', 'original', 'princess', 'switch', 'character', 'world', 'luigi', 'mushroom']

    # Creating the knowledge base
    knowledge_base = build_kb(sig_terms)

    # Printing keys of knowledge base
    print("")
    print(knowledge_base.keys())

    # Commented out because the dictionary is HUGE
    #for x, y in knowledge_base.items():
    #    print(x, y)