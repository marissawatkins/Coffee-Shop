import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
@app.route('/drinks')
def getDrinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'status_code': 200,
            'drinks': drinks,
        })
    except:
        abort(422)
# implement endpoint
# GET /drinks
# it should be a public endpoint
# it should contain only the drink.short() data representation
# returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks or appropriate status code indicating reason for failure

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drink_details(token):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except:
        abort(422)
# implement endpoint
# GET /drinks-detail
# it should require the 'get:drinks-detail' permission
# it should contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
# or appropriate status code indicating reason for failure

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_drinks(token):
    try:
        data = request.get_json()['title'] and request.get_json()['recipe']
        if not data:
            abort(400)
    except (TypeError, KeyError):
        abort(400)

    if Drink.query.filter_by(title=request.get_json()['title']).first():
        abort(409)

    try:
        Drink(title=request.get_json()['title'], recipe=json.dumps(request.get_json()['recipe'])).insert()
        drink = Drink.query.filter_by(title=request.get_json()['title']).first()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 201
    except:
        abort(422)
        
# implement endpoint
# POST /drinks
# it should create a new row in the drinks table
# it should require the 'post:drinks' permission
# it should contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
# or appropriate status code indicating reason for failure

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drinks(token, drink_id):
    try:
        data = request.get_json()['title'] or request.get_json()['recipe']
        if not data:
            abort(400)
    except (TypeError, KeyError):
        abort(400)

    drink = Drink.query.filter_by(id=drink_id).first()
    if not drink:
        abort(404)

    try:
        if request.get_json().get('title'):
            drink.title = request.get_json()['title']
        if request.get_json().get('recipe'):
            drink.recipe = json.dumps(request.get_json()['recipe'])
        drink.update()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except:
        abort(422)

# implement endpoint
# PATCH /drinks/<id>
# where <id> is the existing model id
# it should respond with a 404 error if <id> is not found
# it should update the corresponding row for <id>
# it should require the 'patch:drinks' permission
# it should contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
# or appropriate status code indicating reason for failure

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    # try:
    #     delete_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    #     delete_drink.delete()
    #     return jsonify({
    #         'success': True,
    #         'delete': drink_id
    #     })
    # except:
    #     abort(404)
    drink = Drink.query.filter_by(id=drink_id).first()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        # success = True
        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except:
        abort(422)

# implement endpoint
# DELETE /drinks/<id>
# where <id> is the existing model id
# it should respond with a 404 error if <id> is not found
# it should delete the corresponding row for <id>
# it should require the 'delete:drinks' permission
# returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
# or appropriate status code indicating reason for failure



## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

# implement error handlers using the @app.errorhandler(error) decorator
# each error handler should return (with approprate messages):
@app.errorhandler(404)
def not_found(error):
    return jsonify({
            "success": False, 
            "error": 404,
            "message": "resource not found"
            }), 404
# implement error handler for 404 error handler should conform to general task above 

@app.errorhandler(401)
def authError(error):
    return jsonify({
            "success": False, 
            "error": 401,
            "message": "Authorized error"
            }), 401

@app.errorhandler(403)
def permissionError(error):
    return jsonify({
            "success": False, 
            "error": 403,
            "message": "Permission denied"
            }), 403
# implement error handler for AuthError error handler should conform to general task above 

