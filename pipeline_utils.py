from datetime import date
import os.path
import shutil
import re
import logging
import fasttext


__all__ = ['getFolderPath', 'write_output', 'isEnglish']

logger = logging.getLogger('knowledgegraph')
logger.setLevel(logging.INFO)

model_path_fasttext = './models/fasttext'
model_filename_fasttext = 'lid.176.ftz'
model_filepath_fasttext  = os.path.normpath(os.path.join(os.getcwd(), model_path_fasttext, model_filename_fasttext))
model = fasttext.load_model(model_filepath_fasttext)


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