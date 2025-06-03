import json

with open('lessons.json', 'r') as f:
    data = json.load(f)

for lesson in data['lessons']:
    print(f"Lesson: {lesson['title']}")

    for quiz in lesson['quiz']:  # Loop over the quiz list
        print(quiz['question'])
        for option in quiz['options']:
            print('Options: ', end='')
            print(option, end=' ')

        user_input = input('Correct answer? ')
        if user_input == quiz['answer']:
            print('Correct!')
        else:
            print('Incorrect!')
            print(f"The correct answer is: {quiz['answer']}")

        print()

exit(0)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QVBoxLayout, QPushButton
from sys import argv as sys_argv, exit as sys_exit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PyEducate: School Edition')

if __name__ == '__main__':
    app = QApplication(sys_argv)
    window = MainWindow()
    window.show()
    sys_exit(app.exec())