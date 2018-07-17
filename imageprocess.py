import pytesseract
import pyscreenshot

""" in this file are functions that manage extraction of text from screen """

# eliminate unnecessary pixels from image for better text extraction
def separate_text(img):
    pix = img.load()
    w, h = img.size

    # minimum white value
    threshold = 200
    for i in range(0, w):
        for j in range(0, h):
            try:
                r, g, b = img.getpixel((i, j))
                if r > threshold or g > threshold or b > threshold:
                    pix[i, j] = (255, 255, 255)
            except:
                return "nope"
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
