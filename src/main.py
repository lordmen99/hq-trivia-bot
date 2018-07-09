import src.imageprocess
from src.question import *

# get question & answers from screen
question, answers = src.imageprocess.get_question_and_answers()

# modify question & answers for better results and run time
question, answers = parse_input(question, answers)

# print questions & answers to screen
print(question)
for i in range(0, answers.__len__()):
    print(answers[i])

# print final computed result to standard output
print("answer: " + answers[get_answer(question, answers, False)])

# for custom questions and answers:

# question = input('enter question: ')
#
# i = 0
# answers = {}
# while True:
#     answer = input('enter answer: ')
#     if answer == "":
#         break
#     answers[i] = answer
#     i += 1
