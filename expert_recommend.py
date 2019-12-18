import os
import pickle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
import re
import numpy as np
import argparse
from collections import defaultdict
import metapy

# preprocess text, not called in main() because we used pickle
def preprocess(text):
    stop_words = set(stopwords.words('english'))
    stemmer = SnowballStemmer('english')
    # covert text to lower case
    text = text.lower()
    text = re.sub(r'[^a-z]+', ' ', text)

    # remove whitespace
    text = text.strip()
    # tokenize
    token = word_tokenize(text)

    # remove stop words
    filtered = [i for i in token if not i in stop_words]
    # stemming
    stem = [stemmer.stem(i) for i in filtered]

    return stem

# preprocess title, not called in main() because we used pickle
def preprocess_title():
    # print("read in titles from pickle")
    f = open('pickles/title_pickle', 'rb')
    titles = pickle.load(f)
    preprocessed_titles = {}
    diging = 0
    for file_name in titles.keys():
        title = titles[file_name]
        if diging % 1000 == 0:
            print(diging)
        diging += 1

        processed_title = preprocess(title)
        preprocessed_titles[file_name] = set()
        for i in processed_title:
            preprocessed_titles[file_name].add(i)
    print("dump preprocessed title to pickle")
    f = open('Preprocess_title_pickle', 'wb')
    pickle.dump(preprocessed_titles, f)
    f.close()

def load_pickles():
    f = open('pickles/filename_list_pickle', 'rb')
    filenames = pickle.load(f)

    f = open('pickles/title_pickle', 'rb')
    titles = pickle.load(f)

    # f = open('pickles/abstract_pickle', 'rb')
    # abstracts = pickle.load(f)

    # f = open('pickles/introduction_pickle', 'rb')
    # intros = pickle.load(f)

    # f = open('pickles/body_pickle', 'rb')
    # bodies = pickle.load(f)

    f = open('pickles/authors_pickle', 'rb')
    authors = pickle.load(f)

    f = open('pickles/author_profile_pickle', 'rb')
    author_profile = pickle.load(f)

    f = open('pickles/preprocess_title_pickle', 'rb')
    processed_titles = pickle.load(f)

    return filenames, titles, authors, author_profile, processed_titles

# build author profiles that contains the following:
# key is author name
# value contains affiliation, email, total citation count, paper count,
# as well as the list of papers with respective citation count

# not called in main() because we dump the profile with pickle
def build_author_profile():
    f = open('pickles/authors_pickle', 'rb')
    authors = pickle.load(f)
    authorProfile = defaultdict(dict)
    paperDict = defaultdict(list)
    for file in authors:
        for author in authors[file]:
            paperDict[author[0]].append(file)
            if "email" not in authorProfile[author[0]]:
                authorProfile[author[0]]["email"] = defaultdict(int)
    #             authorProfile[author[0]]["email"] = set([])
    #         authorProfile[author[0]]["email"].add(author[1])
            if author[1] != "":
                authorProfile[author[0]]["email"][author[1]] += 1
            if "affiliation" not in authorProfile[author[0]]:
                authorProfile[author[0]]["affiliation"] = defaultdict(int)
    #             authorProfile[author[0]]["affiliation"] = set([])
    #         authorProfile[author[0]]["affiliation"].add(author[2])
            if author[2] != "" :
                authorProfile[author[0]]["affiliation"][author[2]] += 1

    f = open('pickles/title_pickle', 'rb')
    fileToTitle = defaultdict(str)
    titleToFile = defaultdict(str)
    titles = pickle.load(f)
    for file in titles:
        fileToTitle[file] = titles[file]
        titleToFile[titles[file]] = file

    f = open('pickles/refer_pickle', 'rb')
    refers = pickle.load(f)
    paperCount = defaultdict(int)
    for file in refers:
        for paper in refers[file]:
            if titleToFile[paper] == '':
                continue
            paperCount[titleToFile[paper]] += 1

    for author in paperDict:
        papers = paperDict[author]
        authorProfile[author]["paperCount"] = len(papers)
        authorProfile[author]["papers"] = defaultdict(dict)
        citationCount = 0
        for paper in papers:
            authorProfile[author]["papers"][paper] = paperCount[paper]
            citationCount += paperCount[paper]
        authorProfile[author]["citationCount"] = citationCount

    # output most listed affiliation and email for each author
    for author in authorProfile:
        affCount = 0
        affName = ""
        for affiliation in authorProfile[author]["affiliation"]:
            print(authorProfile[author])
            if authorProfile[author]["affiliation"][affiliation] > affCount:
                affCount = authorProfile[author]["affiliation"][affiliation]
                affName = affiliation
        authorProfile[author]["affiliation"] = affName
        emailCount = 0
        emailName = ""
        for email in authorProfile[author]["email"]:
            if authorProfile[author]["email"][email] > emailCount:
                emailCount = authorProfile[author]["email"][email]
                emailName = email
        authorProfile[author]["email"] = emailName

    f = open('pickles/author_profile_pickle', 'wb')
    pickle.dump(authorProfile, f)
    f.close()

# check if a query is close to the title of a paper
def title_query_match(query, processed_titles, titles):
    # print("read in processed titles from pickle")
    # f = open('pickles/preprocess_title_pickle', 'rb')
    # processed_titles = pickle.load(f)

    # print("read in titles from pickle")
    # f = open('pickles/title_pickle', 'rb')
    # titles = pickle.load(f)

    match_score = []
    processed_query = preprocess(query)
    n = len(processed_query)

    for file_name in processed_titles.keys():
        title = processed_titles[file_name]

        count = 0
        for i in processed_query:
            if i in title:
                count += 1
        match_score.append((file_name, count))

    match_sorted = sorted(match_score, key=lambda x: -x[1])

    counts = [0] * n

    zero_pos = len(match_sorted)
    for i in range(len(match_sorted)):
        if match_sorted[i][1] == 0:
            zero_pos = i
            break
        else:
            counts[match_sorted[i][1] - 1] += 1
    match_sorted_larger_than_zero = match_sorted[0: zero_pos]
    scores = [x for _, x in match_sorted_larger_than_zero]

    mean_score = np.mean(scores)
    # print("mean of score")
    # print(mean_score)
    std_score = np.std(scores)
    # print("std of score")
    # print(std_score)

    result = []

    if n == 1:
        if counts[0] < 5:
            for i, _ in match_sorted_larger_than_zero:
                result.append(i)
    else:
        begin = 0
        for i in range(len(counts) - 1, -1, -1):
            if 0 < counts[i] < 5 and i + 1 > mean_score + 3 * std_score and (i + 1) / n > 0.5:
                while begin < len(match_sorted_larger_than_zero):
                    if match_sorted_larger_than_zero[begin][1] == i + 1:
                        result.append(match_sorted_larger_than_zero[begin][0])
                    else:
                        break
                    begin += 1

    # for i in range(0, min(50, len(match_sorted_larger_than_zero))):
    #     print(titles[match_sorted_larger_than_zero[i][0]], match_sorted_larger_than_zero[i][1])

    return result

# check if bm25 score has top outliers
def search_outliers(bm25_result):
    scores = np.array([x[1] for x in bm25_result])
    upper_quartile = np.percentile(scores, 75)
    lower_quartile = np.percentile(scores, 25)
    IQR = (upper_quartile - lower_quartile)
    outlier_lower_bound_iqr = upper_quartile + IQR * 3
    
    std = np.std(scores)
    mean = np.mean(scores)
    outlier_lower_bound_std = mean + 2 * std
    outlier_lower_bound = min(outlier_lower_bound_iqr, outlier_lower_bound_std)
    # outlier_lower_bound = (outlier_lower_bound_iqr + outlier_lower_bound_std) / 2.0
    outliers = [x[0] for x in bm25_result if x[1] > outlier_lower_bound]
    return outliers

# returns a list of experts
def expert_search(bm25_result, authors, filenames, author_profile, titles):
    bm25_index = [x[0] for x in bm25_result]
    authors_list = []
    author_paper_dict = defaultdict(list)
    for i in bm25_index:
        curr_authors = authors[filenames[i]]
        for a in curr_authors:
            authors_list.append(a[0])
            author_paper_dict[a[0]].append(titles[filenames[i]])
            # if a[0] not in author_paper_dict:
            #     author_paper_dict[a[0]] = titles[filenames[i]]
    authors_list = list(set(authors_list))
    authors_score = defaultdict(list)
    for author_name in authors_list:
        score = 0
        authors_score[author_name].append(author_profile[author_name]['citationCount'] + \
                                    author_profile[author_name]['paperCount'])
        if author_profile[author_name]['paperCount'] == 0:
            authors_score[author_name].append(0)
        else:
            authors_score[author_name].append(author_profile[author_name]['citationCount'] / \
                                    author_profile[author_name]['paperCount'])
    sorted_result = sorted(authors_score.items(), key=lambda k: (-k[1][0], -k[1][1]))[:10]
    sorted_result = [x[0] for x in sorted_result]
    expert_result = []
    for i in sorted_result:
        expert_result.append([i, author_profile[i], author_paper_dict[i]])
    return expert_result

def merge_results(title_match_result, outliers_result):
    merged = []
    result_set = set()
    for i in title_match_result:
        if i not in result_set:
            result_set.add(i)
            merged.append(i)
    for i in outliers_result:
        if i not in result_set:
            result_set.add(i)
            merged.append(i)
    return merged

def get_first_author(top_document_result, authors, filenames, author_profile, titles):
    results = []
    for i in top_document_result:
        results.append([authors[filenames[i]][0][0], author_profile[authors[filenames[i]][0][0]], titles[filenames[i]]])
    return results

def print_results(author_search_result, expert_search_result, f):
    if len(author_search_result) > 5:
        author_search_result = author_search_result[:5]
    if len(expert_search_result) > 15 - len(author_search_result):
        expert_search_result = expert_search_result[:15 - len(author_search_result)]

    author_name_dedup = set()
    for a in author_search_result:
        if a[0] not in author_name_dedup:
            author_name_dedup.add(a[0])
            print('Name: ', a[0], file=f)
            print('Email: ', a[1]['email'], file=f)
            if len(a[1]['affiliation']) > 0:
                print('Affiliation: ', a[1]['affiliation'][:-1], file=f)
            else:
                print('Affiliation: ', a[1]['affiliation'], file=f)
            print('Reason(s) for recommendation:\nFirst author of top matching paper:', file=f)
            print(a[2], file=f)
            print('\n', file=f)

    for a in expert_search_result:
        if a[0] not in author_name_dedup:
            author_name_dedup.add(a[0])
            print('Name: ', a[0], file=f)
            print('Email: ', a[1]['email'], file=f)
            if len(a[1]['affiliation']) > 0:
                print('Affiliation: ', a[1]['affiliation'][:-1], file=f)
            else:
                print('Affiliation: ', a[1]['affiliation'], file=f)
            print('Reason(s) for recommendation:\nExpert in field with {} papers and {} citations'.format(a[1]['paperCount'], a[1]['citationCount']), file=f)
            print('Author of top matching paper(s):', file=f)
            paper_name_dedup = set()
            for paper_name in a[2]:
                if paper_name not in paper_name_dedup:
                    paper_name_dedup.add(paper_name)
                    print(paper_name, file=f)
                # print('\n', file=f)
            print('\n', file=f)


def main(query_name, out_name):
    # preprocess_title()
    filenames, titles, authors, author_profile, processed_titles = load_pickles()
    title_match_result = title_query_match(query_name, processed_titles, titles)
    for i in range(len(title_match_result)):
        filename = title_match_result[i]
        title_match_result[i] = filenames.index(filename)

    idx = metapy.index.make_inverted_index('config.toml')
    ranker = metapy.index.OkapiBM25(k1=1.2, b=0.75, k3=500.0)
    query = metapy.index.Document()
    query.content(query_name)
    bm25_result = ranker.score(idx, query, 100)

    outliers_result = search_outliers(bm25_result)
    top_document_result = merge_results(title_match_result, outliers_result)
    author_search_result = get_first_author(top_document_result, authors, filenames, author_profile, titles)
    expert_search_result = expert_search(bm25_result, authors, filenames, author_profile, titles)

    f = None
    if out_name is not None:
        f = open(out_name, 'w+')
        print('Results written to ' + out_name)
    print_results(author_search_result, expert_search_result, f)
    if out_name is not None:
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run script parameters')
    parser.add_argument('--query', type=str, nargs='?', default='information retrieval',
                        help='Query Name')
    parser.add_argument('--write_to_file', type=int, nargs='?', default=0,
                        help='Write to file named [query].txt')
    args = parser.parse_args()
    out_name = None
    if args.write_to_file == 1:
        out_name = 'output/'+ args.query + '.txt'
    main(args.query, out_name)
