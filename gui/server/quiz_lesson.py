from os.path import join
from json import dumps
from utils.server.storage import load_json, write_json
from utils.server.paths import get_appdata_path
from utils.crypto import get_signature


class QuizBuilder:
    def __init__(self, file_name="lessons.json"):
        self.file_path = join(get_appdata_path(), file_name)
        try:
            self.data = load_json(self.file_path)
        except FileNotFoundError:
            self.data = {"lessons": []}
        self.lesson = None

    def _next_id(self):
        if not self.data["lessons"]:
            return 1
        return max(int(l["id"]) for l in self.data["lessons"]) + 1

    def start(self, title, author="Unknown"):
        # Start a new quiz
        self.lesson = {
            "id": str(self._next_id()),
            "title": title,
            "author": author,
            "quiz": [],
        }

    def add_quiz(self, question, options, answer, points):
        if not self.lesson:
            print("Call start() first")
        self.lesson["quiz"].append(
            {
                "question": question,
                "options": options,
                "answer": answer,
                "points": points,
            }
        )

    def save(self):
        # Save lesson to JSON and add signature.
        self.lesson["type"] = "quiz"
        lesson_copy = dict(self.lesson)
        lesson_id = lesson_copy.pop("id")
        signature = get_signature(dumps(lesson_copy))
        self.lesson["signature"] = signature

        self.data["lessons"].append(self.lesson)
        write_json(self.file_path, self.data)
        print(
            f"✅ Saved lesson {self.lesson['id']} with {len(self.lesson['quiz'])} quizzes"
        )
        return self.lesson["id"]


class QuizHandler:
    def __init__(self, widgets):
        self.widgets = widgets
        self.quiz_list = []
        self.current_index = 0
        self.total_questions = 0

    def start(self, total_questions):
        self.total_questions = total_questions
        self.quiz_list = []
        self.current_index = 0

    def next_question(self):
        w = self.widgets
        question = w["question"].text()
        options = [o.text() for o in w["options"]]
        answer = options[3]  # quiz_op_4 is always the correct answer
        points = w["points"].text()

        self.quiz_list.append(
            {
                "question": question,
                "options": options,
                "answer": answer,
                "points": points,
            }
        )
        self.current_index += 1

        # Clear fields for next question
        if self.current_index < self.total_questions:
            w["question"].clear()
            for o in w["options"]:
                o.clear()
            w["points"].clear()

        return self.current_index >= self.total_questions  # True if all done
