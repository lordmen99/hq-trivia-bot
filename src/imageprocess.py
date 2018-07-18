import pytesseract
import pyscreenshot
from PIL import Image
""" in this file are functions that manage extraction of text from screen """


# eliminate unnecessary pixels from image for better text extraction
def separate_text(img):
    # img = img.resize((img.size[0] * 2, img.size[1] * 2), Image.ANTIALIAS)
    thresh = 200
    img = img.convert('L').point(lambda x: 255 if x > thresh else 0, mode='1')
    # img.show()
    return img


# return extracted text from image
def get_image_text(img):
    img = separate_text(img)
    return pytesseract.image_to_string(img, lang="eng")


# return question and dictionary of answers as extracted from screen
def get_question_and_answers():
    # location of question on screen
    question = get_image_text(pyscreenshot.grab(bbox=(75, 200, 400, 350)))

    answers = {
        # location of answer number '0' on screen
        0: get_image_text(pyscreenshot.grab(bbox=(85, 360, 400, 410))),
        # location of answer number '1' on screen
        1: get_image_text(pyscreenshot.grab(bbox=(85, 425, 400, 475))),
        # location of answer number '2' on screen
        2: get_image_text(pyscreenshot.grab(bbox=(85, 490, 400, 540)))
    }
    return question, answers
