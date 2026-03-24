#################################################################
# FILE : moogle.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex6 2021
# DESCRIPTION: A simple program that...
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: Stackoverflow, kite
# NOTES: ...
#################################################################
import pickle
from typing import List, Dict
import sys
import urllib.parse
import bs4
import requests
from collections import Counter


def get_html(internet_page: str, base_url: str):
    """This function will return the html code of an internet page"""
    full_url = urllib.parse.urljoin(base_url, internet_page)
    response = requests.get(full_url)
    html = response.text
    return html


def create_list_of_internet_pages(index_file: str):
    with open(index_file, 'r') as small_index:
        names_of_internet_pages = small_index.read().splitlines()
    return names_of_internet_pages


def count_links(internet_page_html: str, names_of_internet_pages: List):
    """
    :param internet_page_html: a string of html code of the internet page
    :param names_of_internet_pages: a list of all the internet pages that we
    want to check links to.
    :return: A dictionary containing the number of links to each of the pages
    in the html internet page.
    """
    valid_links_list = []
    soup = bs4.BeautifulSoup(internet_page_html, "html.parser")
    for p in soup.find_all("p"):  # search in all paragraphs of the page.
        for link in p.find_all("a"):  # search in all links in the paragraphs.
            target = link.get("href")
            if target in names_of_internet_pages:
                valid_links_list.append(target)
    num_links_list = Counter(valid_links_list)
    return dict(num_links_list)


def save_as_pickle_file(text_for_file, out_file):
    """This function saves some kind of text to a pickle file."""
    with open(out_file, "wb") as out_pickle:
        pickle.dump(text_for_file, out_pickle)


def crawl(base_url: str, index_file: str, out_file: str):
    """
    This function will create an html code for each internet page and count
    the links to the other pages from each internet page.
    :param base_url: The main url for the site.
    :param index_file: A text file containing all the relative url's
    :param out_file: A name of a pickle file in which we are going to save the
    results in.
    :return: A pickle file with a dictionary of all links to pages from each
    internet page
    """
    traffic_dict = dict()
    names_of_internet_pages = create_list_of_internet_pages(index_file)
    for internet_page in names_of_internet_pages:
        internet_page_html = get_html(internet_page, base_url)
        traffic_dict[internet_page] = count_links(internet_page_html,
                                                  names_of_internet_pages)
    save_as_pickle_file(traffic_dict, out_file)


def calculate_page_rank(new_pages_rank: Dict[str, int],
                        pages_rank: Dict[str, int], internet_page: str,
                        pages_links: Dict[str, Dict[str, int]]):
    """
    The function will calculate the new rank of the internet page given and
    update the new_pages_rank[internet_page] to that value.
    :param new_pages_rank: The page rank of the current iteration.
    :param pages_rank: The pages rank from the last iteration.
    :param internet_page: The internet page for which its new rank is going to
    be calculated.
    :param pages_links: a dictionary containing internet pages and the number
    of links from each page to the others.
    """
    new_pages_rank[internet_page] = 0
    for page in pages_links:
        if internet_page in pages_links[page]:
            total_links_from_page = sum(pages_links[page].values())
            specific_num_of_links = pages_links[page][internet_page]
            new_pages_rank[internet_page] += \
                pages_rank[page] * specific_num_of_links / \
                total_links_from_page


def page_rank(iterations: int, dict_file_links: str, out_file: str):
    """
       This function will calculate the rank of each page. An internet page
       that has more pages pointing to it, will have a higher rank than others.
       The results will be in a dictionary that will be executed as a pickle
       file.
    :param iterations: Number of times to run page_rank
    :param dict_file_links: a file that has a dictionary containing internet
    pages and the number of links from each page to the others.
    :param out_file: A name of a pickle file in which we are going to save the
    results in.
    """
    with open(dict_file_links, "rb") as links_file:
        pages_links = pickle.load(links_file)
    pages_rank = dict.fromkeys(pages_links, 1)
    for i in range(iterations):
        new_pages_rank = pages_rank.copy()
        for internet_page in new_pages_rank:
            calculate_page_rank(new_pages_rank, pages_rank, internet_page,
                                 pages_links)
        pages_rank = new_pages_rank
    save_as_pickle_file(pages_rank, out_file)


def update_all_pages_words(all_pages_words, internet_page, words_amount_dict):
    """
    This function updates the dictionary with all words from all pages by
    adding the words from the specific internet page and the amount of times
    that it appears on that page.
    :param all_pages_words: A dictionary with all the words from all the
    internet pages and the amount of times that they appear in each page.
    :param internet_page: The internet page that we are updating its words to
    the full dictionary.
    :param words_amount_dict: a dictionary containing words from the internet
    and the number of times that they appear in that page.
    """
    for word in words_amount_dict:
        if word in all_pages_words.keys():
            all_pages_words[word][internet_page] = words_amount_dict[word]
        else:
            all_pages_words[word] = {internet_page: words_amount_dict[word]}


def count_page_words(internet_page):
    """This function will check what words are in the internet page given
    and how many times they appear on it and add that to a new dictionary."""
    lst_of_page_words = []
    internet_page_html = get_html(internet_page, base_url)
    soup = bs4.BeautifulSoup(internet_page_html, "html.parser")
    for p in soup.find_all("p"):  # search in all paragraphs of the page.
        content_list: List[str] = p.text.split()
        lst_of_page_words += content_list
    words_amount_dict = Counter(lst_of_page_words)
    return words_amount_dict


def words_dict(base_url: str, index_file: str, out_file: str):
    """This function creates a dictionary with all words in all internet
    pages in the index_file and the value of each word is another
    dictionary that has the internet pages that the word appears in and the
    amount of times that it appears on that page."""
    all_pages_words = dict()
    names_of_internet_pages = create_list_of_internet_pages(index_file)
    for internet_page in names_of_internet_pages:
        words_amount_dict = count_page_words(internet_page)
        update_all_pages_words(all_pages_words, internet_page,
                               words_amount_dict)
    save_as_pickle_file(all_pages_words, out_file)


def execute_content_from_pickle(pickle_file):
    """This function will execute the content of a pickle file"""
    with open(pickle_file, "rb") as a_file:
        content = pickle.load(a_file)
        return content


def find_pages_with_query(query_words_list, words_diction):
    """This function will search for all the internet pages from the index
    file that have all the words in the query. If one of the words in the
    query doesn't exist in the words dictionary, then it will be deleted from
    the list of query words."""
    pages_intrsctn = set()
    for qury in query_words_list:
        if qury in words_diction.keys():
            if len(pages_intrsctn) == 0:
                pages_intrsctn = words_diction[qury].keys()
            new_pages_intrsctn = pages_intrsctn & words_diction[qury].keys()
            pages_intrsctn = new_pages_intrsctn
        else:
            query_words_list.remove(qury)
    return pages_intrsctn


def highest_rank_query_pages(query_pages_with_rank, max_results):
    """
    This function will update the dictionary to have only max_results pages
    with the highest rank.
    :param query_pages_with_rank: The internet pages including all query words
    and their page rank.
    :param max_results: The amount of results we want to get for the query.
    """
    num_of_pages_to_remove = len(query_pages_with_rank) - max_results
    query_pages_rank_sorted = sorted(query_pages_with_rank.values())
    for ind_rank in range(num_of_pages_to_remove):
        for page, rank in query_pages_with_rank.items():
            if rank == query_pages_rank_sorted[ind_rank]:
                del query_pages_with_rank[page]
                break


def find_min_amount_of_word(query_words_list, words_diction, page):
    """This function will check what word from the query appears in the page
    the smallest amount of times, and return the number of times that that word
    is in the page."""
    min_amount = words_diction[query_words_list[0]][page]
    if len(query_words_list) > 1:
        for word_ind in range(1, len(query_words_list)):
            if words_diction[query_words_list[word_ind]][page] < min_amount:
                min_amount = words_diction[query_words_list[word_ind]][page]
    return min_amount


def sort_results_high_to_low(query_pages_with_rank):
    """This function will print the pages and their query results. The pages
    with the highest score will appear first."""
    sorted_results_high_to_low = sorted(set(query_pages_with_rank.values()),
                                        reverse= True)
    for result in sorted_results_high_to_low:
        for page, page_result in query_pages_with_rank.items():
            if result == page_result:
                print(page, result)


def search(query, ranking_dict_file, words_dict_file, max_results):
    """This function will search for a query in all the internet pages and wiil
    print the max_results pages that have all the words of the query in them
    and have the highest score(is the product of the page rank and the minimum
    amount of times that the words appear in the page)"""
    ranking_dict = execute_content_from_pickle(ranking_dict_file)
    words_diction = execute_content_from_pickle(words_dict_file)
    query_words_list = query.split()
    pages_with_query: set = find_pages_with_query(query_words_list,
                                                  words_diction)
    query_pages_with_rank = dict()
    for page in pages_with_query:
        query_pages_with_rank[page] = ranking_dict[page]
    if len(query_pages_with_rank) > max_results:
        highest_rank_query_pages(query_pages_with_rank, max_results)
    for page in query_pages_with_rank:
        min_amount_of_word = find_min_amount_of_word(query_words_list,
                                                     words_diction, page)
        query_pages_with_rank[page] = ranking_dict[page] * \
                                      min_amount_of_word
    sort_results_high_to_low(query_pages_with_rank)


if __name__ == '__main__':
    out_file = sys.argv[4]
    if sys.argv[1] == "crawl":
        base_url = sys.argv[2]
        index_file = sys.argv[3]
        crawl(base_url, index_file, out_file)
    elif sys.argv[1] == "page_rank":
        iterations = int(sys.argv[2])
        dict_file_links = sys.argv[3]
        page_rank(iterations, dict_file_links, out_file)
    elif sys.argv[1] == "words_dict":
        base_url = sys.argv[2]
        index_file = sys.argv[3]
        words_dict(base_url, index_file, out_file)
    elif sys.argv[1] == "search":
        query = sys.argv[2]
        ranking_dict_file = sys.argv[3]
        words_dict_file = sys.argv[4]
        max_results = int(sys.argv[5])
        search(query, ranking_dict_file, words_dict_file, max_results)
