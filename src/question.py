from src.webcrawl import *
import threading
import time
import pyautogui
import pygame
from gtts import gTTS
""" in this file are functions which search for question and return final answer """

sum_lock = threading.Lock()
index_of_answer_lock = threading.Lock()
print_answers_lock = threading.Lock()

# list of scores for each answer
# for example: if first answer has a score of 25
# s[0] will equal 25. one an answer has a score significantly
# higher than the other two, it is said that an answer has been found
s = []
# gets a value of true once an answer has been declared
found = False
# index of answer in 'answers' dictionary
index_of_answer = 0
# holds true if the question is a negative.
# for example:'which of the following is NOT.."
opposite = False
# holds true if answer need to be different than the other two
unique = False
# list of active threads searching for hits
threads = []
# holds true after a click on answer has taken place
answer_clicked = False
answer_played = False


# click location on screen according to answer
def click_answer(answers):
    global index_of_answer
    global answer_clicked

    if answer_clicked:
        return

    answer_clicked = True

    for i in range(0, answers.__len__()):
        if opposite:
            if s[i] < s[index_of_answer]:
                index_of_answer = i
        else:
            if s[i] > s[index_of_answer]:
                index_of_answer = i

    if index_of_answer is 0:
        pyautogui.click((85 + 400) / 2, (360 + 410) / 2)
    elif index_of_answer is 1:
        pyautogui.click((85 + 400) / 2, (425 + 475) / 2)
    elif index_of_answer is 2:
        pyautogui.click((85 + 400) / 2, (490 + 540) / 2)


def play_answer(answers):
    global answer_played

    if answer_played:
        return

    answer_played = True
    tts = gTTS(text=answers[index_of_answer], lang="en")
    tts.save("answer.mp3")
    pygame.mixer.init()
    pygame.init()
    pygame.mixer.music.set_endevent(pygame.USEREVENT)
    pygame.event.set_allowed(pygame.USEREVENT)
    pygame.mixer.music.load('answer.mp3')
    pygame.mixer.music.play()
    pygame.event.wait()


# prints answers with statistics regarding each answer's score
def print_answers(answers):
    global opposite
    global index_of_answer

    click_answer(answers)
    # play_answer(answers)

    try:
        print('%s : %.2f' % (answers[index_of_answer], s[index_of_answer] / sum(s) * 100) + '%')
        for i in range(0, answers.__len__()):
            if i is not index_of_answer:
                print('%s %.2f' % (answers[i], s[i] / sum(s) * 100) + '%')
    except:
        print("couldn't compute an answer")


# add given search terms hits to it's sum of hits
def add_occurrence(i, html_text, search_term, answers, weight):
    global found
    global sum_lock
    global index_of_answer
    global opposite

    if found:
        return
    if unique:
        reg = re.compile(u'missing:.*{0}.*'.format(search_term))
        if reg.findall(html_text).__len__() > 0:
            with index_of_answer_lock:
                index_of_answer = i
            with sum_lock:
                found = True
                with print_answers_lock:
                    print_answers(answers)
                return
    reg = re.compile(
        u' [(.,/"]?' + '[{0}{1}]'.format(search_term[0], search_term[0].lower()) + search_term[1:] + u'[ )!?.",/]')
    if found:
        return

    with sum_lock:
        s[i] += reg.findall(html_text).__len__() * weight

    if opposite:
        less_count = 0
        for j in range(0, answers.__len__()):
            if i != j and s[j] - s[i] > 70:
                less_count = less_count + 1
        if less_count == answers.__len__() - 1:
            with index_of_answer_lock:
                index_of_answer = i
            with sum_lock:
                found = True
                with print_answers_lock:
                    print_answers(answers)
                return

    for j in range(0, answers.__len__()):
        if not opposite and s[i] - s[j] > 80:
            if found:
                return
            with index_of_answer_lock:
                index_of_answer = i
            with sum_lock:
                found = True
                with print_answers_lock:
                    print_answers(answers)


# starts thread searching given url's html
# for each answer in answers. meaning: if there are 3
# answers, each thread will look for hits for a different answer
def search_url(url, answers, weight):
    try:
        # print(url)
        html_text = get_html(url)
        html_text.encode('utf-8')
        for i, search_term in answers.items():
            t = threading.Thread(target=add_occurrence, args=(i, html_text, search_term, answers, weight))
            t.daemon = True

            if found:
                return

            t.start()
    except:
        pass


# search for answers in main google search page
# starts a thread searching page for each answer
def add_google_page_matches(question, answers, weight):
    google_url = google_search_url(question)
    # print(google_url)
    google_html = get_html(google_url)
    for i in range(0, answers.__len__()):
        thread = threading.Thread(target=add_occurrence, args=(i, google_html, answers[i], answers, weight))
        thread.daemon = True
        thread.start()
        threads.append(thread)


# prints answer after 'length' seconds
def print_soon(answers, length):
    time.sleep(length)

    if not found:
        print("***********************************************")
        print("************       estimate        ************")
        print("***********************************************")
        with print_answers_lock:
            print_answers(answers)
        print("***********************************************")


# receives question and answers and returns index of correct answer
def get_answer(question, answers, quick):
    global s
    global index_of_answer
    global opposite

    s = [0 for i in answers]

    # the higher on the page the link is the higher the hit's weight.
    # initial weight is 10 and decreases as links are lower on
    # the google search page
    weight = 10

    # holds list of urls linking to results on first page
    url_list = google_search_result_websites(question)

    # adds hits on google page to sum of hits
    add_google_page_matches(question, answers, weight)

    # timer to click and show result after 3 seconds
    timer = threading.Thread(target=print_soon, args=(answers, 1.7))
    timer.daemon = True
    timer.start()

    for url in url_list:
        # print(url)
        # start thread searching through current url
        thread = threading.Thread(target=search_url, args=(url, answers, weight))
        thread.daemon = True
        if found:
            for thread in threads:
                thread.join()

            return index_of_answer

        threads.append(thread)
        thread.start()
        # decrease next url's hit weight
        weight = weight * 0.7

    for thread in threads:
        thread.join()

    print_answers(answers)
    return index_of_answer


# used when answer is needed in query
def concatenate_answers(answers):
    query = ""
    for i in range(0, answers.__len__()):
        query += answers[i] + " "
    return query


def remove_redundant_words(query):
    query = " " + query + " "
    for word in ['a', 'involving', 'directly', 'An', 'did', 'led', 'him', 'at', 'its', 'around', 'is', 'these', 'does', 'or', 'with', 'Which', 'which', 'has', 'that', 'the', 'what', 'in',
                 'A', 'an', 'of', 'to', 'To', 'How', 'When', 'it', 'to', 'In', 'for', 'known'
        , 'as', 'by', 'these', 'on', 'of', 'and', 'was', 'Who', 'Where', 'What', 'what', 'are', 'would', 'you']:
        to_find = r'\W{0}\W'.format(word)
        reg = re.compile(to_find)
        for match in reg.findall(query):
            loc = query.find(match)
            if loc is not -1:
                query = query[:loc+1] + query[loc+match.__len__()-1:]

    symbols = ['-', '(', ')', '|', ':', '\\', '?', '!', '”', '“']
    for a in symbols:
        query = query.replace(a, '')

    query = query.replace('\n', ' ')

    reg = re.compile(r'\s\s+')

    for match in reg.findall(query):
        query = query.replace(match, ' ')

    return query


def remove_word(query, to_remove):
    return query.replace(to_remove, '')


def parse_input(query, answers):
    global opposite
    global unique

    reg = re.compile(r'.*[wW]hich of the.*')
    # print(query.__len__())
    if reg.findall(query) and query.__len__() < 65:
        query = query + " " + concatenate_answers(answers)

    negatives = [u'NOT', u'NEVER', u"ISN'T"]
    for negative in negatives:
        loc = query.find(negative)
        if loc != -1:
            query = query[:loc] + query[loc + negative.__len__():]
            opposite = True

    symbols = ['/', '(', ')', '|', ':', '\\']
    for i in range(0, answers.__len__()):
        for a in symbols:
            answers[i] = answers[i].replace(a, '')
        if answers[i].__len__() == 0:
            answers.pop(i)
    return remove_redundant_words(query), answers

 