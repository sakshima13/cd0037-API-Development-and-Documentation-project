import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    def paginate_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in questions]
        paginated_questions = questions[start:end]

        return paginated_questions

    @app.route('/categories', methods=["GET"])
    def get_categories():
        if request.method == "GET":
            categories = Category.query.order_by(Category.id).all()
            category_data = {}
            
            for data in categories:
                category_data[data.id] = data.type
                
            if len(category_data) == 0:
                abort(404)
            
            return jsonify({
                'categories': category_data,
                'success': True
            })
    
    @app.route('/questions', methods=['GET'])
    def get_questions():
        categories = Category.query.all()
        question = Question.query.all()
        paginated_questions_list = paginate_questions(request, question)

        if len(paginated_questions_list) == 0:
            abort(404)

        return jsonify({
                "success": True,
                "questions": list(paginated_questions_list),
                "total_questions": len(question),
                'categories': {item.id: item.type for item in categories}
            })

    @app.route('/questions/<int:id>', methods=["DELETE"])
    def delete_question(id):
        selected_ques = Question.query.filter_by(id=id).first()
        
        if selected_ques is None:
            abort(404)
        try:
            selected_ques.delete()
            return jsonify({
                'success': True,
                'question': id
            })
        except: 
            abort(405)
    
    @app.route('/questions', methods=["POST"])
    def add_question():
        try:
            body = request.get_json()
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_category = body.get('category')
            new_difficulty = body.get('difficulty')
            current_question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
                )

            current_question.insert()

            tot_questions = Question.query.all()
            questions_list = paginate_questions(request, tot_questions)

            return jsonify({
            'success': True,
            'created': current_question.id,
            'questions': questions_list,
            'question_created': current_question.question,
            'total_questions': len(tot_questions)
        })
        except:
            abort(422)

    @app.route('/questions/search')
    def search_question():
        search_term = request.args.get('searchTerm')
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        
        print('sel', selection)
        search_questions = paginate_questions(request, selection)
        if search_term == None:
            abort(404)

        return jsonify({
                "success": True,
                "questions": list(search_questions),
                "total_questions": len(selection),
            })
    
    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):

        try:
            selection = Question.query.filter(category_id == Question.category).all()
    
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()

            if category_id > len(categories):
                abort(404)

            return jsonify({
                    "success": True,
                    "questions": list(current_questions),
                    "total_questions": len(selection),
                    "current_category": [cat.type for cat in categories if cat.id == category_id ]
                })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def start_trivia():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = quiz_category['id']

            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()
            question = None
            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except:
            abort(422)
    """
    Error handler routes
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": 'request cannot be processed'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405


    return app

