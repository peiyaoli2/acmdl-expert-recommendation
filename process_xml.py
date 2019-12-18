import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import os
import pickle


def process_A():
    count = 0
    folder = 'input_folder/'
    body_dict = {}
    title_dict = {}
    abstract_dict = {}
    introduction_dict = {}
    for file_name in os.listdir(folder):
        if count % 100 == 0:
            print(count)
        count += 1
        curr_file = folder + file_name
        tree = ET.parse(curr_file)
        root = tree.getroot()
        child_bfs = []
        body = []
        titleStmt = []
        abstract = []
        intro = []
        for child in root:
            child_bfs.append(child)
        while child_bfs:
            node = child_bfs.pop(0)
            if 'body' in str(node.tag).split('}')[1]:
                for child in node:
                    if 'div' in str(child.tag).split('}')[1]:
                        for child_child in child:
                            if 'p' in str(child_child.tag).split('}')[1]:
                                body.append(child_child.text)

            if 'titleStmt' in str(node.tag).split('}')[1]:
                for child in node:
                    if 'title' in str(child.tag).split('}')[1]:
                        titleStmt.append(child.text)

            if 'abstract' in str(node.tag).split('}')[1]:
                for child in node:
                    if 'div' in str(child.tag).split('}')[1]:
                        for child_child in child:
                            if 'p' in str(child_child.tag).split('}')[1]:
                                abstract.append(child_child.text)

            if 'div' in str(node.tag).split('}')[1]:
                if_head_intro = False
                for child in node:
                    if 'head' in str(child.tag).split('}')[1] and 'introduction' in str(child.text).lower():
                        if_head_intro = True
                    elif 'p' in str(child.tag).split('}')[1] and if_head_intro:
                        intro.append(child.text)

            for child in node:
                child_bfs.append(child)

        body_strings = ""
        for i in body:
            body_strings += str(i)
        body_dict[file_name] = body_strings

        title_string = ""
        for i in titleStmt:
            title_string += str(i)
        title_dict[file_name] = title_string

        abstract_string = ""
        for i in abstract:
            abstract_string += str(i)
        abstract_dict[file_name] = abstract_string

        intro_string = ""
        for i in intro:
            intro_string += str(i)
        introduction_dict[file_name] = intro_string

    print("dump body to pickle")
    f = open('body_pickle', 'wb')
    pickle.dump(body_dict, f)
    f.close()

    print("dump title to pickle")
    f = open('title_pickle', 'wb')
    pickle.dump(title_dict, f)
    f.close()

    print("dump abstract to pickle")
    f = open('abstract_pickle', 'wb')
    pickle.dump(abstract_dict, f)
    f.close()

    print("dump introduction to pickle")
    f = open('introduction_pickle', 'wb')
    pickle.dump(introduction_dict, f)
    f.close()


def process_C():
    count = 0
    folder = 'input_folder/'
    for file_name in os.listdir(folder):
        if file_name == '.DS_Store':
            continue
        if count % 100 == 0:
            print(count)
        count += 1
        curr_file = folder + file_name
        tree = ET.parse(curr_file)
        root = tree.getroot()
        child_bfs = []
        refer = []
        listbib = []

        for child in root:
            child_bfs.append(child)

        while child_bfs:
            node = child_bfs.pop(0)
            if 'listBibl' in str(node.tag).split('}')[1]:
                for child in node:
                    if 'biblStruct' in str(child.tag).split('}')[1]:
                        listbib.append(child)
                break

            for child in node:
                child_bfs.append(child)

        child_bfs.clear()
        for bib in listbib:
            for node in bib:
                if 'analytic' in str(node.tag).split('}')[1]:
                    for ana in node:
                        if 'title' in str(ana.tag).split('}')[1]:
                            refer.append(ana.text)

        refer_strings = []
        for i in refer:
            if i:
                refer_strings.append(str(i))

        fold1 = 'refer/'
        name = fold1 + file_name
        f = open(name, "w+")
        for i in refer_strings:
            f.write(i)
            f.write("\n")


def process_keywords():
    count = 0
    folder = 'input_folder/'
    nonKeywords = 0

    for file_name in os.listdir(folder):
        if file_name == '.DS_Store':
            continue
        if count % 100 == 0:
            print(count)
        count += 1
        curr_file = folder + file_name
        tree = ET.parse(curr_file)
        root = tree.getroot()
        child_bfs = []
        keywords = []

        for child in root:
            child_bfs.append(child)

        while child_bfs:
            node = child_bfs.pop(0)
            if 'keywords' in str(node.tag).split('}')[1]:
                for child in node:
                    if 'term' in str(child.tag).split('}')[1]:
                        keywords.append(child.text)
                break

            for child in node:
                child_bfs.append(child)

        child_bfs.clear()

        if not keywords:
            nonKeywords += 1
        
        refer_strings = []
        for i in keywords:
            if i:
                refer_strings.append(str(i))

        fold1 = 'keywords/'
        name = fold1 + file_name
        f = open(name, "w+")
        for i in refer_strings:
            f.write(i)
            f.write("\n")

    print(nonKeywords)


def process_authors():
    folder = "input_folder/"
    out_folder = "authors/"
    count = 0
    authors = {}
    for file_name in os.listdir(folder):
        authors[file_name] = []
        if file_name == '.DS_Store':
            continue

        if count % 1000 == 0:
            print(count)
        count += 1

        curr_file = folder + file_name
        tree = ET.parse(curr_file)
        root = tree.getroot()
        child_bfs = []
        for child in root:
            child_bfs.append(child)

        while child_bfs:
            node = child_bfs.pop(0)
            # get authors
            if 'sourceDesc' in str(node.tag).split('}')[1]:
                analytic = node[0][0]
                for child in analytic:
                    if 'author' in str(child.tag).split('}')[1]:
                        # child is <author>
                        has_name = False
                        for author_property in child:
                            if 'persName' in str(author_property.tag).split('}')[1]:
                                has_name = True
                        if has_name:
                            name = ""
                            email = ""
                            affil = ""
                            for author_property in child:
                                if 'persName' in str(author_property.tag).split('}')[1]:
                                    name_string = ''
                                    for author_name in author_property:
                                        name_string = name_string + author_name.text + ' '
                                    name = name_string.rstrip()
                                if 'email' in str(author_property.tag).split('}')[1]:
                                    email = author_property.text
                                if 'affiliation' in str(author_property.tag).split('}')[1]:
                                    aff_string = ''
                                    for affiliation in author_property:
                                        if 'orgName' in str(affiliation.tag).split('}')[1]:
                                            aff_string = aff_string + affiliation.text + ', '
                                    affil = aff_string.rstrip()
                            author = (name, email, affil)
                            authors[file_name].append(author)
                break
            else:
                for child in node:
                    child_bfs.append(child)

    print("dump authors to pickle")
    f = open('authors_pickle', 'wb')
    pickle.dump(authors, f)
    f.close()


def processPubDate():
    count = 0
    folder = 'input_folder/'
    nonPub = 0
    PubDates = {}

    for file_name in os.listdir(folder):
        if file_name == '.DS_Store':
            continue
        if count % 100 == 0:
            print(count)
        count += 1
        curr_file = folder + file_name
        tree = ET.parse(curr_file)
        root = tree.getroot()
        child_bfs = []
        currDate = ''

        for child in root:
            child_bfs.append(child)

        while child_bfs:
            node = child_bfs.pop(0)
            if 'publicationStmt' in str(node.tag).split('}')[1]:
                for child in node:
                    if 'date' in str(child.tag).split('}')[1]:
                        currDate = child.text
                break

            for child in node:
                child_bfs.append(child)
        if currDate == '':
            nonPub += 1
        PubDates[file_name] = currDate

    print("dump Pub Date to pickle")
    f = open('PubDate_pickle', 'wb')
    pickle.dump(PubDates, f)
    f.close()

    print(nonPub)


def dumpToPickle():
    # count = 0
    # folder = "keywords/"
    # keywords_dict = {}
    # for file_name in os.listdir(folder):
    #     if count % 1000 == 0:
    #         print(count)
    #     count += 1
    #     curr_file = folder + file_name
    #     with open(curr_file, 'r') as f:
    #         keywords_dict[file_name] = []
    #         content = f.readlines()
    #         for i in content:
    #             line = i.strip()
    #             keywords_dict[file_name].append(line)
    # print("dump keywords to pickle")
    # f = open('keywords_pickle', 'wb')
    # pickle.dump(keywords_dict, f)
    # f.close()
    #
    # count = 0
    # folder = "refer/"
    # refer_dict = {}
    # for file_name in os.listdir(folder):
    #     if count % 1000 == 0:
    #         print(count)
    #     count += 1
    #     curr_file = folder + file_name
    #     with open(curr_file, 'r') as f:
    #         refer_dict[file_name] = []
    #         content = f.readlines()
    #         for i in content:
    #             line = i.strip()
    #             refer_dict[file_name].append(line)
    # print("dump reference to pickle")
    # f = open('refer_pickle', 'wb')
    # pickle.dump(refer_dict, f)
    # f.close()

    count = 0
    folder = "authors/"
    authors_dict = {}
    for file_name in os.listdir(folder):
        if file_name == '.DS_Store':
            continue

        authors_dict[file_name] = []
        if count % 1000 == 0:
            print(count)
        count += 1
        curr_file = folder + file_name
        tree = ET.parse(curr_file)
        root = tree.getroot()
        child_bfs = []
        for child in root:
            child_bfs.append(child)

        while child_bfs:
            curr = []
            node = child_bfs.pop(0)
            for child in node:
                curr.append(child.text)
            authors_dict[file_name].append(curr)

    print("dump authors to pickle")
    f = open('authors_pickle', 'wb')
    pickle.dump(authors_dict, f)
    f.close()


def main():
    # process_authors()
    # print("read in authors from pickle")
    # f = open('authors_pickle', 'rb')
    # authors = pickle.load(f)
    # print(1)

    # print("read in refer from pickle")
    # f = open('refer_pickle', 'rb')
    # refer = pickle.load(f)
    # print(1)

    # process_A()

    # print("read in introduction from pickle")
    # f = open('body_pickle', 'rb')
    # intro = pickle.load(f)
    # print(1)

    print("read in Pub date from pickle")
    f = open('PubDate_pickle', 'rb')
    intro = pickle.load(f)
    print(1)


if __name__ == "__main__":
    main()
