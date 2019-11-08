from datetime import date
import os.path
import shutil
import re
import logging
import fasttext
import json
import copy


__all__ = ['getFolderPath', 'write_output', 'isEnglish', 'dedup_relations', 'build_internal_relations_attrs', 'build_internal_entities_attrs', 'convert_to_entities_json','convert_from_entities_json','write_entities_jsonfile','read_entities_jsonfile','build_internal_relationsonly_attrs']

logger = logging.getLogger('knowledgegraph')
logger.setLevel(logging.INFO)

model_path_fasttext = './models/fasttext'
model_filename_fasttext = 'lid.176.ftz'
model_filepath_fasttext  = os.path.normpath(os.path.join(os.getcwd(), model_path_fasttext, model_filename_fasttext))
model = fasttext.load_model(model_filepath_fasttext)

# def build_internal_entities_attrs(sentence, char_start, char_end, new_label):
#     entities = {"entities": [(char_start, char_end, new_label)]}
#     internal_entities_attrs_record = (sentence, entities)
#     return internal_entities_attrs_record

def dedup_relations(relations_arr):
    dedupped_relations = list()
    for relation in relations_arr:
        if relation not in dedupped_relations:
            dedupped_relations.append(relation)
    return dedupped_relations


def build_internal_entities_attrs(sentence, entities_attrs):
    entities = {"entities": entities_attrs}
    internal_entities_attrs_record = (sentence, entities)
    return internal_entities_attrs_record

def build_internal_relations_attrs(sentence, relations_arr):
    relations_map = dict()
    for index, value in enumerate(dedup_relations(relations_arr)):
        relations_map.setdefault(index, value)
    relations = {"relations": relations_map}
    internal_relations_attrs_record = (sentence, relations)
    return internal_relations_attrs_record

def build_internal_relationsonly_attrs(relations_arr):
    relations_map = dict()
    for index, value in enumerate(dedup_relations(relations_arr)):
        relations_map.setdefault(index, value)
    relations = {"relations": relations_map}
    return relations    

def build_internal_all_attrs(sentence, entities_attrs, relations_attrs):
    entities = {"entities": entities_attrs}
    relations = {"relations": relations_attrs}
    internal_all_attrs_record = (sentence, entities, relations)
    return internal_all_attrs_record

    # entities_attrs = list()
    # for entity_attrs in converted_entities_attrs_record[1]['entities']:
    #     char_start = entity_attrs[0]
    #     char_end = entity_attrs[1]
    #     label = entity_attrs[2]
    #     entities_attrs.append((char_start, ))
    #         "char_start": char_start,
    #         "char_end": char_end,
    #         "label": label
    # ]

def convert_to_entities_json(internal_entities_attrs_record):
    converted_entities_attrs_record = copy.deepcopy(internal_entities_attrs_record)
    entities_attrs = list()
    for entity_attrs in converted_entities_attrs_record[1]['entities']:
        entities_attrs.append([entity_attrs[0], entity_attrs[1], entity_attrs[2]])
    converted_entities_attrs_record[1]['entities'] = entities_attrs
    return converted_entities_attrs_record
    # return json.dumps(converted_entities_attrs_record, sort_keys=True, indent=4)



def convert_from_entities_json(converted_entities_attrs_record):
    # internal_entities_attrs_record = json.loads(copy.deepcopy(converted_entities_attrs_record))
    internal_entities_attrs_record = copy.deepcopy(converted_entities_attrs_record)
    # internal_entities_attrs_record[0],internal_entities_attrs_record[1]['entities']['char_start'], internal_entities_attrs_record[1]['entities']['char_end'], internal_entities_attrs_record[1]['entities']['label']
    return build_internal_entities_attrs(internal_entities_attrs_record[0], internal_entities_attrs_record[1]['entities'])

def write_entities_jsonfile(filename, internalobject):
    with open(filename, 'w') as outfile:
        json.dump(convert_to_entities_json(internalobject), outfile)

def read_entities_jsonfile(filename):
    with open(filename, 'r') as infile:
        return convert_from_entities_json(json.load(infile))


def getFolderPath(pipeline_foldername):
    folder_path = os.getcwd() + "/" + pipeline_foldername + "/" + \
        date.today().strftime("%m-%d-%Y")
    logger.info("Using folder path: %s:" % folder_path)
    return folder_path


def write_output(sentences, filepath):
    logger.info("Writing output to file: %s:" % filepath)
    with open(filepath, 'w') as handler:
        handler.writelines("%s" % sentence.text for sentence in sentences)


def isEnglish(text):
    global model
    isEnglish = True
    try:        
        langs = model.predict(text, k=2)
        isEnglish = langs[0][0] == '__label__en'
    except Exception:
        logging.error("exception ", exc_info=1)
    return isEnglish