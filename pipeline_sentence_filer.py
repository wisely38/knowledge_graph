import spacy
import plac
from datetime import date
import os.path
import shutil
import re
import logging
from pipeline_utils import getFolderPath, isEnglish

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

def filter_sentences(doc_to_sents_map, sentences_arr):
    logger.info("Start filtering %s sentences ..."%len(sentences_arr))
    removed_index_list = list()
    filtered_index_list = list()
    for index, sentence in enumerate(sentences_arr):
        if isEnglish(sentence.text):
            has_subject = False
            has_object = False
            has_verb = False
            for tok in doc_to_sents_map.get(sentence):
                has_subject = True if has_subject or tok.dep_ in SUBJ else False
                has_object = True if has_object or tok.dep_ in OBJ else False
                has_verb = True if has_verb or tok.dep_ in VERB else False  
                # if has_subject:
                #     logger.info("index:%d, Found subject:%s"%(index, tok.text))
                #     # print("index:%d, Found subject:%s"%(index, tok.text))
                # if has_object:
                #     logger.info("index:%d, Found object:%s"%(index, tok.text))
                #     # print("index:%d, Found object:%s"%(index, tok.text))
                # if has_verb:
                #     logger.info("index:%d, Found verb:%s"%(index, tok.text))                
                    # print("index:%d, Found verb:%s"%(index, tok.text))                        
            if has_subject & has_object & has_verb:
                filtered_index_list.append(index)
                logger.info("added index:%d"%(index))
                # print("added index:%d"%(index))
            else:
                removed_index_list.append(index)
                result = "subject" if tok.dep_ in SUBJ else "verb" if tok.dep_ in VERB else "object" if tok.dep_ in OBJ else "none"
                logger.info("text:%s, token index:%d, word:%s, dep:%s, type:%s, has_subject:%s, has_object:%s, has_verb:%s" % (sentence.text, index, tok.text, tok.dep_, result, has_subject, has_object, has_verb))
                # print("index:%d, word:%s, dep:%s, type:%s " % (index, tok.text, tok.dep_, result))
        else:
            logger.warn("Skip due to non-English sentence - %s" % sentence)
    filtered_resultset = [x for x in map(sentences_arr.__getitem__, filtered_index_list)]
    removed_resultset = [x for x in map(sentences_arr.__getitem__, removed_index_list)]
    logger.info("Done filtering %f sentences ..."%(len(removed_resultset)/len(sentences_arr)))
    return filtered_resultset, removed_resultset

def write_output(filtered_sents, filtered_filepath):
    logger.info("Writing output to file: %s:"%filtered_filepath)
    with open(filtered_filepath, 'w') as handler:
        handler.writelines("%s" % sentence.text for sentence in filtered_sents)
    logger.info("Writen output to file: %s:"%filtered_filepath)

# needs to run first: python -m spacy download en_core_web_sm
# def main(patterns_loc, text_loc, n=10000, lang="en"):
def main():
    subfoldername = "/staging/" + date.today().strftime("%m-%d-%Y") 
    subfolderpath = os.getcwd() + subfoldername 
    logger.info("Start processing sentence filter from folder:%s..."%subfolderpath)
    if os.path.exists(subfolderpath):
        for filename in os.listdir(subfolderpath):
            if re.match("crawler-output_.+.txt", filename):
                logger.info("Start processing sentence filter for file:%s..."%filename)
                with open(os.path.normpath(os.path.join(os.getcwd(), subfolderpath, filename)), "r") as handler:
                    filtered_filename = filename.replace("crawler-output_", "filtered-output_")
                    removed_filename = filename.replace("crawler-output_","removed-output_")
                    nlp = spacy.load("en_core_web_lg")
                    sentences = handler.readlines()
                    doc_to_sents_map = dict()
                    sentence_spans = list()
                    for section in sentences:
                        doc = nlp(section)
                        sents = [x for x  in doc.sents]
                        for sent in sents:
                            doc_to_sents_map.setdefault(sent, doc)
                        sentence_spans.extend(sents)                    
                    filtered_sents, removed_sents = filter_sentences(doc_to_sents_map, sentence_spans)
                    write_output(filtered_sents, os.path.normpath(os.path.join(os.getcwd(), subfolderpath, filtered_filename)))
                    write_output(removed_sents, os.path.normpath(os.path.join(os.getcwd(), subfolderpath,removed_filename)))
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
            