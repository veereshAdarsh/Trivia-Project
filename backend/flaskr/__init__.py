import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QS_PER_PAGE = 10


# def paginate_questions(request, selection):
#     page = request.args.get('page', 1, type=int)
#     start = (page - 1) * QUESTIONS_PER_PAGE
#     end = start + QUESTIONS_PER_PAGE
#     questions = [question.format() for question in selection]
#     current_questions = questions[start:end]
#     return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
     # To run Server, executing from backend directory:
    # Only one Time:
    # export FLASK_APP=flaskr
    # export FLASK_ENV=development
    # flask run
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"*": {"origins": "*"}})


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    # Fetch all the categorie types from the categories table
    def fetch_categories():
        try:
            categories = Category.query.order_by(Category.type).all()
            
            if len(categories) == 0:
                abort(404)

            res = {
                'success': True,
                'categories': {category.id: category.type for category in categories}
            }

            for category in categories:
                res['categories'][str(category.id)] = category.type

            return jsonify(res)

        except Exception as e:
            print(e)
            return abort(500, 'Internal server error')

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    #Fetch questions from the questions table
    def fetch_questions():
        try:
            pageNum = int(request.args['page'])
        except Exception as e:
            return abort(400)

        begin = (pageNum-1) * QS_PER_PAGE
        end = begin + QS_PER_PAGE

        res = {
            'questions': [],
            'total_questions': -1,
            'categories': {},
            'current_category': "",
            'success': True
        }

        all_QS = []
        filtered_QS = []

        try:
            for question in Question.query.all():
                all_QS.append(question.format())

            for category in Category.query.all():
                res['categories'][str(category.id)] = category.type
        except Exception as e:
            print(e)
            return abort(500, 'Internal server error')

        filtered_QS = all_QS[begin:end]

        if len(filtered_QS) == 0:
            return abort(404)

        res['questions'] = filtered_QS
        res['total_questions'] = len(all_QS)
        res['current_category'] = res['categories'][str(filtered_QS[0]['category'])]

        return jsonify(res)
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<question_id>", methods=['DELETE'])
    
    # Delete question by question id
    def delete_question(QS_ID):
        try:
            question = Question.query.get(QS_ID)
            question.delete()
            return jsonify({
                'success': True,
            }), 200
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=['POST'])
    #Add new question to the database
    def add_new_question():
        body = request.get_json()
        if not ('question' in body and 'answer' in body and 'difficulty' in body and 'category' in body):
            abort(422)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_difficulty = body.get('difficulty')
        new_category = body.get('category')

        try:
            question = Question(question=new_question, answer=new_answer,
                                difficulty=new_difficulty, category=new_category)
            question.insert()
            return jsonify({
                'success': True,
                'created': question.id,
            }), 200
        except:
            abort(422, 'Unprocessable')


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    # Search question by question name
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        if search_term:
            search_results = Question.query.filter(Question.question.ilike("%{}%".format(request.json['searchTerm']))).all

            if len(search_results) == 0:
                return abort(404)

            res = {
                'success': True,
                'questions': [question.format() for question in search_results],
                'total_questions': len(search_results),
                'current_category': None
            }
            return res


        response = {
            'questions': [],
            'total_questions': -1,
            'current_category': "",
            'success': True
        }

        # all_questions = []

        # try:
        #     for question in questions:
        #         all_questions.append(question.format())

        # except Exception as e:
        #     print(e)
        #     return abort(500)

        # if len(all_questions) == 0:
        #     return jsonify()

        # current_category = Category.query.filter(Category.id == all_questions[0]['category']).one()

        # response['questions'] = all_questions
        # response['total_questions'] = len(all_questions)
        # response['current_category'] = current_category.type

        # return jsonify(response)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    #Filter question by category id
    def fetch_questions_by_category(category_id):

        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()

            if len(questions) == 0:
                return abort(404)

            res = {
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions),
                'current_category': category_id
            }
            return res
        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    #Play quiz
    def play_quiz():
        try:
            body = request.get_json()
            if not ('category' in body and 'questions' in body):
                abort(422)

            category = body.get('category')
            questions = body.get('questions')

            if category['type'] == 'click':
                available_QS = Question.query.filter(Question.id.notin_((questions))).all()
            else:
                available_QS = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((questions))).all()

            new_QS = available_QS[random.randrange(0, len(available_QS))].format() if len(available_QS) > 0 else None

            res = {
                'success': True,
                'question': new_QS
            }
            return res

        except:
            abort(422, 'Unprocessable')


        # try:
        #     body = request.get_json()
        #     if not ('quiz_category' in body and 'previous_questions' in body):
        #         abort(422)

        #     category = body.get('quiz_category')
        #     previous_questions = body.get('previous_questions')

        #     if category['type'] == 'click':
        #         available_questions = Question.query.filter(
        #             Question.id.notin_((previous_questions))).all()
        #     else:
        #         available_questions = Question.query.filter_by(
        #             category=category['id']).filter(Question.id.notin_((previous_questions))).all()

        #     new_question = available_questions[random.randrange(
        #         0, len(available_questions))].format() if len(available_questions) > 0 else None

        #     return jsonify({
        #         'success': True,
        #         'question': new_question
        #     })
        # except:
        #     abort(422)



    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # Requested resource not found error
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Requested resource not found!"
        }), 404

    #Unprocessable error
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable!"
        }), 422

    #Bad request error
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request!"
        }), 400

    #Internal server error
    @app.errorhandler(500)
    def internal_server(error):
        return jsonify({
            'success': False,
            'error': 500, 
            'message': 'Internal server error. Something went wrong!'
        }), 500
    
    return app

