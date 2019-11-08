import pytest
import sys
import json
sys.path.append("..") 
from pipeline_utils import build_internal_entities_attrs, convert_to_entities_json, convert_from_entities_json, build_internal_relations_attrs, dedup_relations

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

@pytest.fixture
def internal_relations_json_data():
    return [
        ("The benchmark includes mainly investment-grade corporate bonds denominated in USD, EUR and GBP, with exposure to bonds denominated in any given currency limited to below 50%\n", {"relations": [[[14, 22, "VERT", "include"], [57, 62, "OBJECT", "bond"], [4, 13, "SUBJECT", "benchmark"]],[[14, 22, "VERT", "has"], [57, 62, "OBJECT", "bond"], [4, 13, "SUBJECT", "benchmark"]]]}),
        ("The benchmark includes mainly investment-grade corporate bonds denominated in USD, EUR and GBP, with exposure to bonds denominated in any given currency limited to below 50%\n", {"relations": [[[14, 22, "VERT", "include"], [57, 62, "OBJECT", "bond"], [4, 13, "SUBJECT", "benchmark"]],[[14, 22, "VERT", "include"], [57, 62, "OBJECT", "bond"], [4, 13, "SUBJECT", "benchmark"]]]}),
    ]

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

def test_build_internal_relations_attrs(internal_relations_json_data):
    internal_relations = build_internal_relations_attrs(internal_relations_json_data[0][0], internal_relations_json_data[0][1]['relations'])
    assert len(internal_relations[1]['relations']) == 2
    internal_relations = build_internal_relations_attrs(internal_relations_json_data[1][0], internal_relations_json_data[1][1]['relations'])
    assert len(internal_relations[1]['relations']) == 1    
    
def test_dedup_relations(internal_relations_json_data):
    dedupped = dedup_relations(internal_relations_json_data[1][1]['relations'])
    assert len(dedupped)<len(internal_relations_json_data[1][1]['relations'])