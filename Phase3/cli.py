import os
from elasticsearch import Elasticsearch
import json
import numpy as np


def insert_to_index(json_array, es):
    for i in json_array:
        es.index(index='paper_index', id=i['id'], body={'paper': i})


def delete_from_index(json_array, es):
    for i in json_array:
        try:
            es.delete(index='paper_index', id=i['id'])
        except:
            pass


def Nmaxelements(list1, N):
    final_list = []
    list1 = [[list1[i], i] for i in range(len(list1))]

    for i in range(0, N):
        max1 = [0, 0]

        for j in range(len(list1)):

            if list1[j][0] > max1[0]:
                max1 = list1[j];

        list1.remove(max1);
        final_list.append(max1)
    return final_list


def calculate_hits(graph):
    n = len(graph)

    auth = np.array([1 for i in range(n)])
    hub = np.array([1 for i in range(n)])

    for i in range(10):

        for j in range(n):
            hub[j] = 0
            for k in range(n):
                if graph[j][k] > 0:
                    hub[j] += auth[k]

        for j in range(n):
            auth[j] = 0
            for k in range(n):
                if graph[k][j] > 0:
                    auth[j] += hub[k]

        hub = hub / np.linalg.norm(hub, 1)
        auth = auth / np.linalg.norm(auth, 1)
    return auth


def index_articles(json_array):
    ids_dict = {}
    index = 0

    x = 0
    for article in json_array:

        article_id = article['id']
        if article_id not in ids_dict:
            ids_dict[article_id] = index
            index += 1

    return ids_dict


def page_rank(graph, alpha: float = 0.1):
    N = graph.shape[1]

    graph = [(1 - alpha) * i + alpha / N if sum(i) != 0 else np.array([1 / N]) for i in graph]

    x = np.array([1 / N] * N)

    for i in range(200):
        x = x @ graph

    return x


def get_server_address():
    elastic_address = input("Please enter address of running Elasticsearch, -1 for default value. (localhost:9200)\n")
    try:
        int(elastic_address)
        elastic_address = 'localhost:9200'
    except:
        pass
    return elastic_address


def get_json_address():
    json_address = input("Please enter the name of json crawled file, or -1 to use default path. (crawled.json)\n")
    try:
        p = int(json_address)
        json_address = 'crawled.json'
    except:
        pass

    input_file = open(json_address)
    return json.load(input_file)


def print_commands():
    print('Enter the number of the command you want to execute, then press enter.')
    print('1 : Crawl data.')
    print('2 : Elastic search setup.')
    print('3 : Calcualte page rank.')
    print('4 : Search the database.')
    print('5 : Ranking the authors.')
    print('6 : Exit!')


def create_query(weight, query):
    search_param = {

        "query": {
            "bool": {
                "should": [
                    {
                        "function_score": {
                            "query": {
                                "match": {
                                    "paper.title": query['title']
                                }
                            },

                            "weight": weight['title'],
                            "score_mode": "multiply"
                        }
                    },

                    {
                        "function_score": {
                            "query": {
                                "range": {
                                    "paper.date": {"gte" : query['pub_date']}
                                }
                            },

                            "weight": weight['pub_date'],

                            "score_mode": "multiply"
                        }
                    },
                    {
                        "function_score": {
                            "query": {
                                "match": {
                                    "paper.abstract": query['abstract']
                                }
                            },

                            "weight": weight['abstract'],

                            "score_mode": "multiply"
                        }
                    },

                ]

            }
        }
    }
    search_param['size'] = 10
    return search_param


def elastic_setup(es, json_array):
    while True:

        print('Enter 1 to delete the indexed data from elasticsearch.')
        print('Enter 2 to index data of the json file to elasticsearch.')
        print('Enter 3 to delete the index completely from elasticsearch.')
        print('Enter other keys to go back to main menu.')

        action = int(input('Choose your action\n'))
    
        if action == 2:
            print('inserting data into index ...')
            insert_to_index(json_array, es)
            print('insertion done.')
        elif action == 1:
            print('deleting data from index ...')

            delete_from_index(json_array, es)
            print('deletion done.')

        elif action == 3:
            print('deleting index ...')
            try:
                es.indices.delete(index='paper_index', ignore=[400, 404])
            except:
                print('No such index')
            print('delition done.')
        else:
            break


def calculate_and_add_pageRank(es, json_array, alpha):
    adj_matrix = [[0 for i in range(len(json_array))] for j in range(len(json_array))]

    ids_dict = {}
    index = 0
    for article in json_array:
        article_id = article['id']
        if article_id not in ids_dict:
            ids_dict[article_id] = index
            index += 1

    for article in json_array:
        article_id = article['id']

        for id in article['references']:

            if id in ids_dict:
                adj_matrix[ids_dict[article_id]][ids_dict[id]] += 1

    adj_matrix = np.array(adj_matrix)
    adj_matrix = np.array([i / sum(i) if sum(i) > 0 else i for i in adj_matrix])

    pageRank = page_rank(adj_matrix, 0.1)
    for i in range(len(json_array)):
        json_array[i]['page_rank'] = pageRank[i]
    delete_from_index(json_array, es)
    insert_to_index(json_array, es)

    print('pageRank is:')
    print(pageRank)


def search(es, weight, query, page_rank_use):
    search_param = create_query(weight, query)
    if page_rank_use == 1:
        search_param['sort'] = [{"paper.page_rank": "desc"}]

    response = es.search(index="paper_index", body=search_param)
    for i in response['hits']['hits']:
        print(i['_source'], '\n\n')


def find_top_authors(articles, num_of_authors):
    adj_matrix = [[0 for i in range(len(articles) * 3)] for j in range(len(articles) * 3)]

    author_dict = {}
    author_name = []
    index = 0
    ids_dict = index_articles(articles)
    

    for article in articles:
        authors = article['authors']

        article_id = article['id']

        for author in authors:

            if author not in author_dict:
                author_name.append(author)
                author_dict[author] = index
                index += 1

        for id in article['references']:

            if id in ids_dict:
                for author in articles[ids_dict[id]]['authors']:
                    if author not in author_dict:
                        author_dict[author] = index
                        author_name.append(author)
                        index += 1
                    for auths in authors:
                        adj_matrix[author_dict[auths]][author_dict[author]] = 1

    adj_matrix = [i[:index] for i in adj_matrix[:index]]
    auth = calculate_hits(adj_matrix)
    top_authors = Nmaxelements(auth, num_of_authors)
    top_authors = [[author_name[i[1]], i[0]] for i in top_authors]
    print(top_authors)


while True:

    print_commands()
    command = 0

    try:
        command = int(input())
        if command <= 0 or command >= 8:
            print('invalid command!')
            continue
    except:
        print('invalid command!')
        continue

    if command == 6:
        break
    elif command == 1:
        os.system('scrapy runspider crawler.py')

    elif command == 2:
        json_array = get_json_address()
        elastic_address = get_server_address()

        es = Elasticsearch(elastic_address)
        elastic_setup(es, json_array)


    elif command == 3:

        json_array = get_json_address()
        elastic_address = get_server_address()

        es = Elasticsearch(elastic_address)
        alpha = float(input("Please enter value of alpha.\n"))

        calculate_and_add_pageRank(es, json_array, alpha)



    elif command == 4:
        elastic_address = get_server_address()

        es = Elasticsearch(elastic_address)
        weight = {}
        query = {}
        weight['title'] = float(input('Please enter weight of title in query.\n'))
        weight['abstract'] = float(input('Please enter weight of abstract in query.\n'))
        weight['pub_date'] = float(input('Please enter weight of publish dated in query.\n'))

        query['title'] = input('Please enter title query.\n')
        query['abstract'] = input('Please enter abstract query.\n')
        query['pub_date'] = int(input('Please enter publish date query.\n'))

        page_rank_use = int(input('Do you want to use pageRank in ranking too?\n'))

        search(es, weight, query, page_rank_use)



    elif command == 5:

        num_of_authors = int(input('Please enter number of desired top authors.\n'))
        articles = get_json_address()
        find_top_authors(articles, num_of_authors)


    else:
        print('invalid command')
