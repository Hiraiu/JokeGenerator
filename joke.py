#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# task_2.py

# University of Zurich
# Department of Computational Linguistics

# Authors: Irina Camelia Stroescu, Fortesa Zeqiri

import time
from typing import List, Tuple, Dict
import re
import random
import csv
from lxml import etree
import json


class Joke:
    """The Joke object contains the joke, and some metadata on that joke. One can compare the jokes by upvotes"""
    def __init__(self, raw_joke):
        self.raw_joke = raw_joke
        self.author = self.raw_joke[0]
        self.link = self.raw_joke[1]
        self.joke = self.raw_joke[2]
        self.rating = int(self.raw_joke[3])
        self.time = self.raw_joke[4]

        self.sentences_joke = self.split_into_sentences()
        self.tokenized_joke = self._tokenize()
        self.filtered_joke = self.filter_profanity()[0]
        self.num_profanities = self.filter_profanity()[1]
        self.xml = self._get_xml_repr()
        self.dict = self._get_json_repr()

    def split_into_sentences(self) -> List[str]:
        """Split text into sentences"""
        output = re.findall(r' ?([^.!?\n]+[.?!]*|\n)', self.joke)
        return output

    def _tokenize(self) -> List[List[str]]:
        """Tokenize all the words in the sentences"""
        output = []
        for sentence in self.sentences_joke:
            tokenized_sentence = re.findall(r'([\w\']+|\?|\.|\n|,|!)', sentence)
            output.append(tokenized_sentence)
        return output

    def filter_profanity(self, filename="profanities.txt") -> Tuple[List[List[str]], int]:
        """Filter out all the profanity"""

        output = []

        # Count number of profanities
        num_profanities = 0

        # Read in profanity file
        with open(filename, "r", encoding = 'utf-8')as file:
            profanities = file.read().split("\n")

        for sentence in self.tokenized_joke:
            no_profanity = True
            text_sentence = " ".join(sentence)
            for profanity in profanities:

                # Check if there is profanity in the sentence
                if profanity in text_sentence:
                    profanity_in_text = True
                else:
                    profanity_in_text = False

                while profanity_in_text:
                    num_profanities += 1
                    no_profanity = False

                    # Find the index of the profanity
                    index = text_sentence.index(profanity)
                    front = text_sentence[:index - 1]

                    # Find the words that need to be replaced
                    num_words_before_profanity = len(front.split(" "))
                    num_profanity_words = len(profanity.split(" "))
                    profanity_in_sentence = sentence[num_words_before_profanity: num_words_before_profanity + num_profanity_words]

                    # Replace the profanity with '#'
                    replacement = ["#" * len(word) for word in profanity_in_sentence]

                    # Construct new sentence composed of the parts with and without profanity
                    new_sent = []
                    new_sent.extend(sentence[:num_words_before_profanity])
                    new_sent.extend(replacement)
                    new_sent.extend(sentence[num_words_before_profanity + len(replacement):])
                    text_sentence = " ".join(new_sent)
                    sentence = new_sent

                    # Check if there is still profanity in the sentence
                    if profanity in text_sentence:
                        profanity_in_text = True

                    else:
                        profanity_in_text = False
                        output.append(new_sent)

            # Add sentence immediately if there are no profanities in the sentence
            if no_profanity:
                output.append(sentence)
        return output, num_profanities

    def tell_joke(self):
        if len(self.filtered_joke) > 1:
            build_up = self.filtered_joke[:-1]
            punch_line = self.filtered_joke[-1:]

            print(self.pretty_print(build_up))
            time.sleep(1)
            print(self.pretty_print(punch_line))
        else:
            print(self.pretty_print(self.filtered_joke))

    @staticmethod
    def pretty_print(joke) -> str:
        """Print in a humanly readable way"""
        output = ""
        for sentence in joke:
            output += " ".join(sentence) + " "
        return output

    def _get_xml_repr(self) -> etree.Element:
        """Get the xml representation of the Joke with all its attributes as nodes"""
        # creating the tree structure
        root = etree.Element("joke")
        text = etree.SubElement(root, "text")
        author = etree.SubElement(root, "author")
        rating = etree.SubElement(root, "rating")
        link = etree.SubElement(root, "link")
        time = etree.SubElement(root, "time")
        profanity_score = etree.SubElement(root, "profanity_score")
        # filling in the tree structures with the attributes of the joke class
        text.text = self.joke
        author.text = self.author
        rating.text = str(self.rating)
        link.text = self.link
        time.text = self.time
        profanity_score.text = str(self.num_profanities)
        return root

    # creating a dictionary with the elements of the joke
    def _get_json_repr(self) -> dict:
        """Get the JSON representation"""
        dictionary = {"author": self.author, "link": self.link, 'joke': self.joke,
                      "rating": self.rating, "time": self.time, "profanity score": self.num_profanities}
        return dictionary

    def __repr__(self):
        """Allows for printing"""
        return self.pretty_print(self.filtered_joke)

    def __eq__(self, other):
        """Equal rating"""
        return self.rating == other.rating

    def __lt__(self, other):
        """less than rating"""
        return self.rating > other.rating

    def __gt__(self, other):
        """greater than rating"""
        return self.rating < other.rating

    def __le__(self, other):
        """less than or equal rating"""
        return self.rating >= other.rating

    def __ge__(self, other):
        """greater than or equal rating"""
        return self.rating <= other.rating


class JokeGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.jokes = self.make_jokes_objects()

    def make_jokes_objects(self):
        with open(self.filename, "r", encoding="utf-8") as lines:
            # distinguishing between the .csv and .json files with if statements
            if ".csv" in self.filename:
                lines = csv.reader(lines, delimiter=',')
                jokes = [Joke(row) for row in lines]
                return jokes
            elif ".json" in self.filename:
                jsondict = json.load(lines)
                jokeslist = []
                # accessing the nested dictionary (the author, rating, text etc of the jokes)
                for item in jsondict.items():
                    attrlist = []
                    # accessing only the values of the nested dictionary (so the actual text of the joke)
                    for value in item[1].values():
                        attrlist.append(value)
                    # storing the jokes one by one
                    jokeslist.append(attrlist)
                # creating the joke object for each joke
                jokes = [Joke(element) for element in jokeslist]
                return jokes

    def generate_jokes(self):
        for joke in self.jokes:
            if len(joke.filtered_joke) > 1:
                joke.tell_joke()
            time.sleep(10)

    def random_joke(self):
        joke = random.sample(self.jokes, 1)[0]
        joke.tell_joke()

    def save_jokes_xml(self, outfile) -> None:
        """Save all the jokes of the Generator in their xml representation to the outfile"""
        tree = etree.Element("jokes")
        for element in self.jokes:
            tree.append(element.xml)
        f = open(outfile, "w", encoding="utf-8")
        xml_bytes = etree.tostring(tree, encoding="utf-8", pretty_print=True, xml_declaration=True)
        xml_str = xml_bytes.decode("utf-8")
        for line in xml_str:
            f.write(line)
        f.close()
        return etree.tostring(tree, encoding="Unicode", pretty_print=True)

    def save_jokes_json(self, outfile: str) -> None:
        """Save all the jokes of the Generator in their json representation to the outfile"""
        dictionary = {}
        with open(outfile, 'w', encoding="utf-8") as f:
            values = [j.dict for j in self.jokes]
            keys = range(len(self.jokes))
            for number in keys:
                dictionary[number] = values[number]
            json.dump(dictionary, f, indent=2)


def main():
    gen = JokeGenerator("reddit_dadjokes.csv")
    gen.save_jokes_json('reddit_dadjokes.json')
    gen.save_jokes_xml('reddit_dadjokes.xml')
    gen_json = JokeGenerator("reddit_dadjokes.json")
    gen_json.random_joke()


if __name__ == "__main__":
    main()
