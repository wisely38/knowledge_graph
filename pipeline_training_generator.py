import spacy
import plac
from datetime import date
import os.path
import shutil
import re
import logging
from pipeline_utils import getFolderPath

logger = logging.getLogger('knowledgegraph')
logger.setLevel(logging.INFO)

# @plac.annotations(
#     patterns_loc=("Path to gazetteer", "positional", None, str),
#     text_loc=("Path to Reddit corpus file", "positional", None, str),
#     n=("Number of texts to read", "option", "n", int),
#     lang=("Language class to initialise", "option", "l", str),
# )

SUBJ = ["nsubj","nsubjpass"] 
VERB = ["ROOT"] 
OBJ = ["dobj", "pobj", "dobj"] 



def custom_seg(doc):
    prev = doc[0].text
    length = len(doc)
    for index, token in enumerate(doc):
        if (token.text == '.' and boundary.match(prev) and index!=(length - 1)):
            doc[index+1].sent_start = False
        prev = token.text
    return doc


# needs to run first: python -m spacy download en_core_web_sm
# def main(patterns_loc, text_loc, n=10000, lang="en"):
def main():
    # subfoldername = "/staging/" + date.today().strftime("%m-%d-%Y") 
    # subfolderpath = os.getcwd() + subfoldername
    subfolderpath = getFolderPath('staging')
    logger.info("Start processing sentence filter from folder:%s..."%subfolderpath)
    if os.path.exists(subfolderpath):
        for filename in os.listdir(subfolderpath):
            if re.match("crawler-output_.+.txt", filename):
                logger.info("Start processing training data generator for file:%s..."%filename)
                with open(os.path.normpath(os.path.join(os.getcwd(), subfolderpath, filename)), "r") as handler:
                    filtered_filename = filename.replace("crawler-output_","filter-output_")
                    nlp = spacy.load("en_core_web_sm")
                    boundary = re.compile('^[,]$')
                    nlp.add_pipe(custom_seg, before='parser')
                    handler.readlines()
                    doc = nlp(text)
                    for sentence in doc.sents:
                        print(sentence.text)
                    for tok in doc:
                        if tok.pos_.strip() != "PUNCT" and tok.pos_.strip() != "SPACE":
                            print(tok.i, tok, "[", tok.dep_, " -> ",tok.head.text,"/",tok.pos,"/", tok.pos_, "/",doc.text.index(tok.text),":",doc.text.index(tok.text)+len(tok.text),"]")
# 0 The [ det  ->  fund / 90 / DET / 0 : 3 ]
# 1 HSBC [ compound  ->  fund / 96 / PROPN / 4 : 8 ]
# 2 GIF [ compound  ->  fund / 96 / PROPN / 9 : 12 ]
# 3 Global [ compound  ->  Bond / 96 / PROPN / 13 : 19 ]
# 4 Lower [ compound  ->  Bond / 96 / PROPN / 20 : 25 ]
# 5 Carbon [ compound  ->  Bond / 96 / PROPN / 26 : 32 ]
# 6 Bond [ compound  ->  fund / 96 / PROPN / 33 : 37 ]
# 7 fund [ nsubjpass  ->  designed / 92 / NOUN / 38 : 42 ]
# 8 is [ auxpass  ->  designed / 87 / AUX / 43 : 45 ]
# 9 designed [ ROOT  ->  designed / 100 / VERB / 46 : 54 ]
# 10 to [ aux  ->  provide / 94 / PART / 55 : 57 ]
# 11 provide [ xcomp  ->  designed / 100 / VERB / 58 : 65 ]
# 12 potential [ amod  ->  gains / 84 / ADJ / 66 : 75 ]
# 13 long [ amod  ->  term / 84 / ADJ / 76 : 80 ]
# 15 term [ compound  ->  gains / 92 / NOUN / 81 : 85 ]
# 16 gains [ dobj  ->  provide / 92 / NOUN / 86 : 91 ]
# 17 with [ prep  ->  gains / 85 / ADP / 92 : 96 ]
# 18 a [ det  ->  footprint / 90 / DET / 17 : 18 ]
# 19 reduced [ amod  ->  footprint / 100 / VERB / 99 : 106 ]
# 20 carbon [ compound  ->  footprint / 92 / NOUN / 107 : 113 ]
# 21 footprint [ pobj  ->  with / 92 / NOUN / 114 : 123 ]


# training data
# TRAIN_DATA = [
#     ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
#     ("I like London and Berlin.", {
#      "entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
# ]





                    sentences = handler.readlines()
                    doc_to_sents_map = dict()
                    sentence_spans = list()
                    for section in sentences:
                    #     for sub_section in section:
                        doc = nlp(section)
                        sents = [x for x  in doc.sents]
                        for sent in sents:
                            doc_to_sents_map.setdefault(sent, doc)
                        sentence_spans.extend(sents)                    
                    filtered_sents = filter_sentences(doc_to_sents_map, sentence_spans)
                    write_output(filtered_sents, os.path.normpath(os.path.join(os.getcwd(), subfolderpath,filtered_filename)))
                    logger.info("Done processing sentence filter for file:%s..."%filename)


if __name__ == "__main__":
    main()
    # if False:
    #     import cProfile
    #     import pstats

    #     cProfile.runctx("plac.call(main)", globals(), locals(), "Profile.prof")
    #     s = pstats.Stats("Profile.prof")
    #     s.strip_dirs().sort_stats("time").print_stats()
    # else:
    #     plac.call(main)
            
