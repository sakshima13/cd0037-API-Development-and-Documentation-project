import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:a@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        self.new_question = {
            'question': 'que',
            'answer': 'ans',
            'difficulty': 1,
            'category': 4
        }
        
        self.quiz = {
    "previous_questions": [],
    "quiz_category": {
        "type": "Science",
        "id": "1"
}
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    # test get categories
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        
    def test_categories_not_available(self):
        response = self.client().get('//categories')        
        self.assertEqual(response.status_code, 404)
        
    # test get questions
    def test_get_all_question(self):
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_question_not_available(self):
        response = self.client().get('//questions')        
        self.assertEqual(response.status_code, 404)
        
    def test_delete_question(self):
        
        response = self.client().delete('/questions/2')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        
    def test_delete_question_not_available(self):
        response = self.client().delete('/questions/1')
        self.assertEqual(response.status_code, 404)
        
    def test_add_question(self):
        response = self.client().post('/questions', json=self.new_question)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        
    def test_add_question_fail(self):
        response = self.client().post('/questions')
        self.assertEqual(response.status_code, 422)
        
    def test_search_question(self):
        response = self.client().post('/questions/search?searchTerm=what')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        
    def test_search_question_not_available(self):
        response = self.client().post('/questions/search')
        self.assertEqual(response.status_code, 404)
        
    def test_category_question(self):
        response = self.client().get('/categories/1/questions')

        data = json.loads(response.data)
        
    def test_category_question_not_available(self):
        response = self.client().get('/categories/10/questions')
        self.assertEqual(response.status_code, 404)
        
    def test_start_quiz(self):
        response = self.client().post('/quizzes', json=self.quiz)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        
    def test_quiz_not_started(self):
        response = self.client().post('/quizzes')
        self.assertEqual(response.status_code, 422)
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()