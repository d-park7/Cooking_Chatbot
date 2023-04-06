import requests
import urllib.request
import re
import os
import pickle
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from itertools import islice
from functools import reduce



STARTER_URL = "https://www.epicurious.com" 


def crawler():
    reqs = requests.get(STARTER_URL)
    data = reqs.text
    soup = BeautifulSoup(data, features="lxml")
    with open('urls.txt', 'w') as file:
        for link in soup.find_all('a'):
            link_str = str(link.get('href'))
            if 'recipe' in link_str or 'ingredient' in link_str:
                file.write(link_str + '\n')

def scrapper():
    """Scraps the STARTER_URL
    
    Input: none
    Returns: none
    
    Side effect: creates urls.txt file and writes scrapped urls to that file"""
    with open('urls.txt', 'r') as file:
        for my_url in file:
            if 'http' not in my_url:
                my_url = STARTER_URL + my_url
            html = urllib.request.urlopen(my_url)
            soup = BeautifulSoup(html, features='lxml')
            data = soup.findAll(text=True)
            result = filter(visible, data)
            temp_list = list(result)      # list from filter
            temp_str = ' '.join(temp_list)
            write_text_to_file(my_url.replace('/', '').strip() + '.txt', temp_str, "w")


def sentence_tokenization(text: str): 
    text = re.sub(r'[\t\n]',' ', text.lower())     # remove tabs and newlines
    sentences = sent_tokenize(text)
    return sentences


def parse_text_file(file_name: str) -> str:
    """Parse a text file into a string
    Input: file name
    Returns: string
    """
    try:
        with open(file_name) as file:
            contents = file.read()
    except OSError as err:
        print("OS error:" , err)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
    finally:
        return contents


def extract_important_terms(contents: str):
    """Extract most frequent words from contents
    
    Input: string
    Returns: dict of item: count
    """
    contents = re.sub(r'[/+=&.?!,:;()©\“”’\'\-\n\d]',' ', contents.lower())
    tokens = word_tokenize(contents)
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if not t in stop_words]
    count_tokens_dict = {t:tokens.count(t) for t in set(tokens)}
    return count_tokens_dict 


def write_text_to_file(file_name: str, text: str, mode: str):
    with open(os.path.join(os.getcwd(), file_name), mode) as file:
        file.write(text)
        

def visible(element):
    """Helper function to determin if an element is visible"""
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


def reducer(accumulator, element):
    """Helper function to combine the list of dicts"""
    for key, value in element.items():
        accumulator[key] = accumulator.get(key, 0) + value
    return accumulator


if __name__ == "__main__":
    crawler()
    scrapper()


    list_important_terms = list()
    with open('urls.txt', 'r') as file:
        for my_url in file:
            if 'http' not in my_url:
                my_url = STARTER_URL + my_url
            contents = parse_text_file(my_url.replace('/', '').strip() + '.txt')
            sentences = sentence_tokenization(contents)
            for sentence in sentences:
                write_text_to_file(my_url.replace('/', '').strip() + '.out.txt', sentence + '\n', "a")
            
            important_terms = extract_important_terms(contents)
            list_important_terms.append(dict(important_terms))
            
        

    # combine the most frequent terms of each page into a sorted dict
    total = reduce(reducer, list_important_terms, {})
    sorted_dict = sorted(total.items(), key=lambda x:x[1], reverse=True)
    top_words = dict(islice(dict(sorted_dict).items(), 45))
    print(top_words)
    
    knowledge_base = list() 
    with open('urls.txt', 'r') as file:
        for my_url in file:
            if 'http' not in my_url:
                my_url = STARTER_URL + my_url
            with open(my_url.replace('/', '').strip() + '.out.txt', 'r') as readfile:
                for sentence in readfile:
                    if "cake" in sentence:
                        knowledge_base.append(sentence)
                    elif "rice" in sentence:
                        knowledge_base.append(sentence)
                    elif "chicken" in sentence:
                        knowledge_base.append(sentence)
                    elif "food" in sentence:
                        knowledge_base.append(sentence)
                    elif "chocolate" in sentence:
                        knowledge_base.append(sentence)
                    elif "cook" in sentence:
                        knowledge_base.append(sentence)
                    elif "cookie" in sentence:
                        knowledge_base.append(sentence)
                    elif "baking" in sentence:
                        knowledge_base.append(sentence)
                    elif "sauce" in sentence:
                        knowledge_base.append(sentence)
                    elif "cream" in sentence:
                        knowledge_base.append(sentence)

    pickle.dump(knowledge_base, open('knowledge_base.p', 'wb'))
