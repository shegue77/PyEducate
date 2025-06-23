# FIRST VERSION, CLI ONLY

import json

with open('lessons.json', 'r') as f:
    data = json.load(f)

print(data)
print(type(data))

for lesson in data['lessons']:
    print(f"Lesson: {lesson['title']}")

    for quiz in lesson['quiz']:  # Loop over the quiz list
        print(quiz['question'])
        print('Options: ', end='')
        for option in quiz['options']:
            print(option, end=' ')

        user_input = input('Correct answer? ')
        if user_input == quiz['answer']:
            print('Correct!')
        else:
            print('Incorrect!')
            print(f"The correct answer is: {quiz['answer']}")

        print()