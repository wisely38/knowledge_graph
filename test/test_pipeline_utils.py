import pytest
import sys
import json
sys.path.append("..") 
from pipeline_utils import build_internal_entities_attrs, convert_to_entities_json

@pytest.fixture
def training_data():
    TRAIN_DATA = [
        ("Who is Shaka Khan?", {"entities": [(7, 17, "PERSON")]}),
        ("I like London and Berlin.", {"entities": [(7, 13, "LOC"), (18, 24, "LOC")]}),
    ]
    return TRAIN_DATA

@pytest.fixture
def internal_training_data(training_data):
    return build_internal_entities_attrs(training_data[0][0],training_data[0][1]['entities'])


def test_build_internal_entities_attrs(training_data):
    internal_repre = build_internal_entities_attrs(training_data[0][0],training_data[0][1]['entities'])
    assert internal_repre[0] == training_data[0][0]
    assert internal_repre[1] == {"entities": [(7, 17, "PERSON")]}

def test_convert_to_entities_json(internal_training_data, training_data):
    json_repre = convert_to_entities_json(internal_training_data)
    assert json_repre[0] == internal_training_data[0]
    assert json_repre[1] == training_data[0]['entities'][0]
