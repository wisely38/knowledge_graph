import pytest
import sys
import json
sys.path.append("..") 
from pipeline_utils import build_internal_entities_attrs, convert_to_entities_json, convert_from_entities_json

@pytest.fixture
def training_data():
    TRAIN_DATA = [
        ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
        ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
        ("the HSBC Global Asset Management website", {"entities": [(5, 8, "ORG"), (3,9, "NEWENTITY")]})        
    ]
    return TRAIN_DATA

@pytest.fixture
def internal_training_data(training_data):
    return  [
        ("Who is Shaka Khan?", {"entities": [[7, 17, "PERSON"]]},{"new_entity":False},[]),
        ("I like London and Berlin.", {"entities": [[7, 13, "LOC"], [18, 24, "LOC"]]},{"new_entity":False},[]),
        ("the HSBC Global Asset Management website", {"entities": [[5, 8, "ORG"], [3,9, "NEWENTITY"]]},{"relations": [[5, 8, "ORG"], [3,9, "NEWENTITY"], [3,9, "NEWENTITY"]]},{"new_entity":True},[{"by_nounchunk":True, "new_entity":"the HSBC Global Asset Management website"}])        
    ]

@pytest.fixture
def entities_json_data(internal_training_data):
    return convert_to_entities_json(internal_training_data[1])

def test_build_internal_entities_attrs(internal_training_data):
    internal_repre = build_internal_entities_attrs(internal_training_data[0][0],internal_training_data[0][1]['entities'])
    assert internal_repre[0] == internal_training_data[0][0]
    assert internal_repre[1] == {"entities": [[7, 17, "PERSON"]]}

def test_build_internal_entities_attrs_mutlipleentities(internal_training_data):
    internal_repre = build_internal_entities_attrs(internal_training_data[1][0], internal_training_data[1][1]['entities'])
    objstr = json.dumps(internal_repre)
    obj = json.loads(objstr)
    assert obj[0] == internal_training_data[1][0]
    assert obj[1] == {"entities": [[7, 13, "LOC"], [18, 24, "LOC"]]}

def test_convert_to_entities_json(internal_training_data):
    json_repre = convert_to_entities_json(internal_training_data[1])
    assert json_repre[0] == internal_training_data[1][0]
    for index in range(len(json_repre[1]['entities'][0])):
        assert json_repre[1]['entities'][0][index] == internal_training_data[1][1]['entities'][0][index]

def test_convert_from_entities_json(entities_json_data):
    internal_repre = convert_from_entities_json(entities_json_data)
    assert entities_json_data[0] == internal_repre[0]
    for index in range(len(entities_json_data[1]['entities'][0])):
        assert entities_json_data[1]['entities'][0][index] == entities_json_data[1]['entities'][0][index]