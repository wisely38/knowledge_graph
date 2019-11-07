import spacy
from datetime import date
import os.path
import shutil
import re
import logging
import json
from pipeline_utils import getFolderPath, build_internal_entities_attrs, convert_to_entities_json, convert_from_entities_json, write_entities_jsonfile, read_entities_jsonfile


logger = logging.getLogger('knowledgegraph')
logger.setLevel(logging.INFO)

SUBJ = ["nsubj","nsubjpass"] 
VERB = ["ROOT"] 
OBJ = ["dobj", "pobj", "dobj"] 



# def custom_seg(doc):
#     prev = doc[0].text
#     length = len(doc)
#     for index, token in enumerate(doc):
#         if (token.text == '.' and boundary.match(prev) and index!=(length - 1)):
#             doc[index+1].sent_start = False
#         prev = token.text
#     return doc

# training data
# TRAIN_DATA = [
#     ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
#     ("I like London and Berlin.", {
#      "entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
# ]

# train_data = [
#     ("Uber blew through $1 million a week", [(0, 4, 'ORG')]),
#     ("Android Pay expands to Canada", [(0, 11, 'PRODUCT'), (23, 30, 'GPE')]),
#     ("Spotify steps up Asia expansion", [(0, 8, "ORG"), (17, 21, "LOC")]),
#     ("Google Maps launches location sharing", [(0, 11, "PRODUCT")]),
#     ("Google rebrands its business apps", [(0, 6, "ORG")]),
#     ("look what i found on google! 😂", [(21, 27, "PRODUCT")])]

# What entities do you need?
# asset type - etf, indices,

# product type - structured/off-shore fund
# Risk level/type - credit risk/liquidity risk
# company - HSBC


# new entity label
LABEL_ASSET_TYPE = "ASSET_TYPE"
LABEL_RISK_TYPE = "RISK_TYPE"
LABEL_EXPERTISE_TYPE = "EQUITY"
LABEL_ASSETTYPE = "FIXED_INCOME"


# training data
# Note: If you're using an existing model, make sure to mix in examples of
# other entity types that spaCy correctly recognized before. Otherwise, your
# model might learn the new type, but "forget" what it previously knew.
# https://explosion.ai/blog/pseudo-rehearsal-catastrophic-forgetting
# TRAIN_DATA = [
#     (
#         "Horses are too tall and they pretend to care about your feelings",
#         {"entities": [(0, 6, LABEL)]},
#     ),
#     ("Do they bite?", {"entities": []}),
#     (
#         "horses are too tall and they pretend to care about your feelings",
#         {"entities": [(0, 6, LABEL)]},
#     ),
#     ("horses pretend to care about your feelings", {"entities": [(0, 6, LABEL)]}),
#     (
#         "they pretend to care about your feelings, those horses",
#         {"entities": [(48, 54, LABEL)]},
#     ),
#     ("horses?", {"entities": [(0, 6, LABEL)]}),
# ]






# needs to run first: python -m spacy download en_core_web_sm
# def main(patterns_loc, text_loc, n=10000, lang="en"):
def main():
    # subfoldername = "/staging/" + date.today().strftime("%m-%d-%Y") 
    # subfolderpath = os.getcwd() + subfoldername
    training_filename = 'preparation-training_data.json'
    subfolderpath = getFolderPath('staging')
    logger.info("Start processing sentence filter from folder:%s..."%subfolderpath)
    if os.path.exists(subfolderpath):
        training_data = list()
        for filename in os.listdir(subfolderpath):
            if re.match("filtered-output_.+.txt", filename):
                logger.info("Start processing training data generator for file:%s..."%filename)
                with open(os.path.normpath(os.path.join(os.getcwd(), subfolderpath, filename)), "r") as handler:
                    # training_filename = filename.replace("filtered-output_","preparation-output_").replace('.txt','.json')
                    nlp = spacy.load("en_core_web_lg")                    
                    # nlp.add_pipe(custom_seg, before='parser')
                    sentences = handler.readlines()
                    count = 1
   
                    for section in sentences:
                        doc = nlp(section)
                        logger.debug("Start printing entities %s"%count)
                        doc_ents = list()
                        for ent in doc.ents:
                            logger.debug(ent.text, ent.start,ent.end,ent.start_char, ent.end_char, ent.label_, doc[ent.start].ent_type_)
                            doc_ents.append((ent.start_char, ent.end_char, ent.label_))
                        training_data.append(build_internal_entities_attrs(doc.text, doc_ents))
                        logger.debug("Done entities %s"%count)
                        logger.debug("Start printing chunks %s"%count)
                        for chunk in doc.noun_chunks:
                            logger.debug(chunk.text, chunk.start,chunk.end,chunk.start_char, chunk.end_char, chunk.label_)
                            logger.debug("Start printing span_ents %s"%count)
                            for span_ent in chunk.ents:
                                logger.debug(span_ent.text, span_ent.start,span_ent.end,span_ent.start_char, span_ent.end_char, span_ent.label_, doc[span_ent.start].ent_type_)
                                training_data.append(build_internal_entities_attrs(doc.text, span_ent.start_char, span_ent.end_char, span_ent.label_))
                            logger.debug("Done span_ents %s"%count)
                        logger.debug("Done chunks %s"%count)         
                        count +=1
                    # for tok in doc:
                    #     if tok.pos_.strip() != "PUNCT" and tok.pos_.strip() != "SPACE":
                    #         print(tok.i, tok, "[", tok.dep_, " -> ",tok.head.text,"/",tok.pos,"/", tok.pos_, "/",doc.text.index(tok.text),":",doc.text.index(tok.text)+len(tok.text),"]")
        with open(training_filename, 'w') as fp:
            fp.write(
                '[' +
                ',\n'.join(json.dumps(i) for i in training_data) +
                ']\n')
        logger.info("Writen file:%s"%training_filename)  


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







                    # sentences = handler.readlines()
                    # doc_to_sents_map = dict()
                    # sentence_spans = list()
                    # for section in sentences:
                    # #     for sub_section in section:
                    #     doc = nlp(section)
                    #     sents = [x for x  in doc.sents]
                    #     for sent in sents:
                    #         doc_to_sents_map.setdefault(sent, doc)
                    #     sentence_spans.extend(sents)                    
                    # filtered_sents = filter_sentences(doc_to_sents_map, sentence_spans)
                    # write_output(filtered_sents, os.path.normpath(os.path.join(os.getcwd(), subfolderpath,filtered_filename)))
                    # logger.info("Done processing sentence filter for file:%s..."%filename)


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
            
