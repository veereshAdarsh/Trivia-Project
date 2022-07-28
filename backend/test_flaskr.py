import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_USER, DB_PASSWORD, TEST_DB

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app.s"""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = TEST_DB #"trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD,'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Validate pagination questions response
    def test_paginate_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    # Test to validate the requested question is not found
    def test_404_requesting_questions_beyond_valid_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Requested resource not found!')

    # Test to search non existing categorie
    def test_404_sent_requesting_non_existing_category(self):
        response = self.client().get('/categories/9999')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Requested resource not found!')

    # Test to delete question
    def test_delete_question(self):
        question = Question(question='new question', answer='new answer',difficulty=1, category=1)
        question.insert()
        question_id = question.id
        response = self.client().delete(f'/questions/{question_id}')
        data = json.loads(response.data)
        question = Question.query.filter(Question.id == question.id).one_or_none()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        self.assertEqual(question, None)

    # Test to delete non existing question
    def test_422_sent_deleting_non_existing_question(self):
        response = self.client().delete('/questions/a')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable!')

    # Test to create new question and answer
    def test_create_question(self):
        new_question = {
            'question': 'new question',
            'answer': 'new answer',
            'difficulty': 1,
            'category': 1
        }
        total_questions_before = len(Question.query.all())
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        total_questions_after = len(Question.query.all())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    # Ttest to add question with invalid format
    def test_422_add_question(self):
        new_question = {
            'question': 'new_question',
            'answer': 'new_answer',
            'category': 1
        }
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable!")

    # Test to search question
    def test_search_questions(self):
        new_search = {'searchTerm': 'a'}
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    # Test to search question partial text which is not present
    def test_404_search_question(self):
        new_search = {
            'searchTerm': '',
        }
        response = self.client().post('/questions/search', json=new_search)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Requested resource not found!")

    # Test to get questions
    def test_get_category_questions(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    # Test to get question which is not present
    def test_404_get_questions_per_category(self):
        response = self.client().get('/categories/a/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Requested resource not found!")

    # Test to play quiz
    def test_404_play_quiz(self):
        new_quiz = {'previous_questions': []}
        response = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable!")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()