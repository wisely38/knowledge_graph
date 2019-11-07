from datetime import date
import os.path
import shutil
import re
import logging
import fasttext


__all__ = ['getFolderPath', 'write_output', 'isEnglish']

logger = logging.getLogger('knowledgegraph')
logger.setLevel(logging.INFO)


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
    isEnglish = True
    try:
        model = fasttext.load_model('lid.176.ftz')
        langs = model.predict(text, k=2)
        isEnglish = langs[0][0] == '__label__en'
    except Exception:
        logging.error("exception ", exc_info=1)
    return isEnglish