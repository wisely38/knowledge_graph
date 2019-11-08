import spacy
from datetime import date
import os.path
import shutil
import re
import logging
import json
from spacy.matcher import Matcher 
from pipeline_utils import getFolderPath, build_internal_entities_attrs, convert_to_entities_json, convert_from_entities_json, write_entities_jsonfile, read_entities_jsonfile, build_internal_all_attrs, build_internal_relations_attrs, build_internal_relationsonly_attrs


logger = logging.getLogger('knowledgegraph')
logger.setLevel(logging.INFO)

SUBJ = ["nsubj","nsubjpass"] 
VERB = ["ROOT"] 
OBJ = ["dobj", "pobj", "dobj"]

OBJ = ["risk", "pobj", "dobj"] 

# new entity label
LABEL_ASSET_TYPE = "ASSET"
LABEL_RISK_TYPE = "RISK"
LABEL_PRODUCT_TYPE = "PRODUCT"
LABEL_NEWENTITY = "NEW_ENTITY"


LABEL_RELATION = "RELATION"
LABEL_SUBJECT = "SUBJECT"
LABEL_VERB = "VERB"
LABEL_OBJECT = "OBJECT"

ENTITY_TYPE_RISK = ["risk"]
ENTITY_TYPE_ASSET = ["etf", "equity", "equities", "fixed income", "indice", "index", "bond"] 
ENTITY_TYPE_PRODUCT = ["service", "fund", "porfolio"] 

def extract_objectsubject(token):
    if token.lemma_ == "-PRON-":
        return token.text
    else:
        return token.lemma_

# Get entity type annotation for trainning by looking for seed words
def get_entity_type(text):
    regex_risk = re.compile(".*" + "|".join(ENTITY_TYPE_RISK) + ".*", re.DOTALL)
    regex_asset = re.compile(".*" + "|".join(ENTITY_TYPE_ASSET) + ".*", re.DOTALL)
    regex_product = re.compile(".*" + "|".join(ENTITY_TYPE_PRODUCT) + ".*", re.DOTALL)
    if regex_risk.match(text.lower()):
        return LABEL_RISK_TYPE
    elif regex_asset.match(text.lower()):
        return LABEL_ASSET_TYPE
    elif regex_product.match(text.lower()): 
        return LABEL_PRODUCT_TYPE
    else:
        return LABEL_NEWENTITY


# needs to run first: python -m spacy download en_core_web_lg
def main():
    subfoldername = "/staging/" + date.today().strftime("%m-%d-%Y") 
    subfolderpath = os.getcwd() + subfoldername
    training_filename = 'preparation-training_data.json'
    relations_token_filename = 'preparation-relations_token_data.json'
    relations_compound_filename = 'preparation-relations_compound_data.json'
    logger.info("Start processing sentence filter from folder:%s..."%subfolderpath)
    if os.path.exists(subfolderpath):
        training_data = list()
        relation_token_data = list()
        relation_compound_data = list()
        for filename in os.listdir(subfolderpath):
            if re.match("filtered-output_.+.txt", filename):
                logger.info("Start processing training data generator for file:%s..."%filename)
                with open(os.path.normpath(os.path.join(os.getcwd(), subfolderpath, filename)), "r") as handler:
                    nlp = spacy.load("en_core_web_lg")                    
                    sentences = handler.readlines()
                    count = 1
   
                    for section in sentences:
                        doc = nlp(section)
                        logger.info("Start printing entities %s"%count)
                        doc_ents = list()
                        for ent in doc.ents:
                            logger.debug(ent.text, ent.start,ent.end,ent.start_char, ent.end_char, ent.label_, doc[ent.start].ent_type_)
                            doc_ents.append((ent.start_char, ent.end_char, ent.label_))
                        logger.info("Done entities %s"%count)
                        logger.info("Start printing chunks %s" % count)
                        # we will determine 
                        subject_attrs = list()
                        verb_attrs=list()
                        object_attrs = list()
                        doc_relations_by_token = list()
                        doc_relations_by_compound = list()
                        for tok in doc:
                            is_subject = True if tok.dep_ in SUBJ else False
                            is_object = True if tok.dep_ in OBJ else False
                            is_verb = True if tok.dep_ in VERB else False
                            if is_subject:
                                subject_attrs.append(tok.idx)
                                subject_attrs.append(tok.idx + len(tok))
                                subject_attrs.append(extract_objectsubject(tok))
                            if is_object:
                                object_attrs.append(tok.idx)
                                object_attrs.append(tok.idx + len(tok))
                                object_attrs.append(extract_objectsubject(tok))
                            if is_verb:
                                verb_attrs.append(tok.idx)
                                verb_attrs.append(tok.idx + len(tok))
                                verb_attrs.append(tok.lemma_)
                            if is_subject or is_object or is_verb:                                                     
                                logger.info("word:%s, dep:%s, is_subject:%s, is_object:%s, is_verb:%s" % (tok.text, tok.dep_, is_subject, is_object, is_verb))    
                                logger.info("token start:%s, token end:%s"%(tok.idx,tok.idx+len(tok)))                                              

                        for chunk in doc.noun_chunks:
                            logger.info(chunk.text, chunk.start,chunk.end,chunk.start_char, chunk.end_char, chunk.label_)
                            logger.info("Start processing noun chunks %s" % count)
                            chunk_relations_by_token = list()
                            chunk_relations_by_compound = list()
                            if len(subject_attrs) > 2:
                                doc_ents.append((subject_attrs[0], subject_attrs[1], get_entity_type(subject_attrs[2])))
                                if subject_attrs[0]>=chunk.start_char and subject_attrs[1]<=chunk.end_char: 
                                    chunk_relations_by_compound.append((chunk.start_char, chunk.end_char, LABEL_SUBJECT, chunk.lemma_, get_entity_type(chunk.lemma_)))
                                chunk_relations_by_token.append((subject_attrs[0], subject_attrs[1], LABEL_SUBJECT, subject_attrs[2], get_entity_type(subject_attrs[2])))                                                                  
                            if len(verb_attrs) > 2:
                                chunk_relations_by_token.append((verb_attrs[0], verb_attrs[1], LABEL_VERB, verb_attrs[2]))
                                chunk_relations_by_compound.append((verb_attrs[0], verb_attrs[1], LABEL_VERB, verb_attrs[2]))
                            if len(object_attrs) > 2:
                                doc_ents.append((object_attrs[0], object_attrs[1], get_entity_type(object_attrs[2])))
                                if object_attrs[0] >= chunk.start_char and object_attrs[1] <= chunk.end_char:
                                    chunk_relations_by_compound.append((chunk.start_char, chunk.end_char, LABEL_OBJECT, chunk.lemma_,get_entity_type(chunk.lemma_)))
                                chunk_relations_by_token.append((object_attrs[0], object_attrs[1], LABEL_OBJECT, object_attrs[2], get_entity_type(object_attrs[2])))
                            doc_relations_by_token.append(chunk_relations_by_token)
                            doc_relations_by_compound.append(chunk_relations_by_compound)                                  

                            logger.info("Done processing noun chunks %s"%count)
                        training_data.append(build_internal_entities_attrs(doc.text, list(set(doc_ents))))
                        relation_token_data.append(build_internal_relationsonly_attrs(doc_relations_by_token))
                        relation_compound_data.append(build_internal_relationsonly_attrs(doc_relations_by_compound ))
                        logger.info("Done chunks %s"%count)         
                        count +=1

        #Writes training data with new annotations for further machine model building
        with open(os.path.join(getFolderPath('staging'), training_filename), 'w') as fp:
            output_text = '[' + ',\n'.join(json.dumps(i) for i in training_data) + ']\n'
            fp.write(output_text.encode('utf8').decode('utf8'))
        logger.info("Writen file:%s" % training_filename)
        
        #Writes relations data with subjects and objects represented by tokens 
        with open(os.path.join(getFolderPath('staging'), relations_token_filename), 'w') as fp:
            output_text = '[' + ',\n'.join(json.dumps(i) for i in relation_token_data) + ']\n'
            fp.write(output_text.encode('utf8').decode('utf8'))            
        logger.info("Writen file:%s" % relations_token_filename)
        
        #Writes relations data with subjects and objects represented by compound tokens 
        with open(os.path.join(getFolderPath('staging'), relations_compound_filename), 'w') as fp:
            output_text = '[' + ',\n'.join(json.dumps(i) for i in relation_compound_data) + ']\n'
            fp.write(output_text.encode('utf8').decode('utf8'))            
        logger.info("Writen file:%s"%relations_compound_filename)  

    else:
        logger.error("Cannot find folder path:%s"%subfolderpath)  

if __name__ == "__main__":
    main()