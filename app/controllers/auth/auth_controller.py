from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
import validators
from app.models.users import User
from app.extensions import db, bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth = Blueprint('auth', __name__, url_prefix='/api')

# User registration
@auth.route('/register', methods=['POST'])
def register_user():
    data = request.json
    # Getting values from the incoming request
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    password = data.get('password')
    user_type = data.get('user_type')

    # Request body must include the following.
    if not name or not email or not phone or not password or not user_type:
        return jsonify({'Error':'All fields are required'}),HTTP_400_BAD_REQUEST  # response returned in json format
    
    if len(password) < 8:
        return jsonify({'Error':'Password is too short.'}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({'Error':'Invalid email address.'}), HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(email = email).first() is not None: # Email should not be already in use.
        return jsonify({"Error":"Email is already in use."}), HTTP_409_CONFLICT
    
    if User.query.filter_by(phone = phone).first() is not None: # Contact should not be already in use. Name of value in model = variable name in controller.
        return jsonify({"Error":"Contact is already in use."}), HTTP_409_CONFLICT
    
    # Logic that stores the new user to the database.
    try:
        # Encrypting the password
        hashed_password = bcrypt.generate_password_hash(password)
        # Defining new instance, with the variable new_user on the user model class.
        new_user = User(name = name, 
                        email = email, 
                        phone = phone, 
                        address = address,
                        password = hashed_password, # To enhance security.
                        user_type = user_type)
        db.session.add(new_user)
        db.session.commit()
        
        # Returning a personalised message to show that a new user has been succesfully created.
        return jsonify({
            'Message': new_user.name + " has been created as an " + new_user.user_type,
            'User' :{
                "id" : new_user.id,
                "name" : new_user.name,
                "email" : new_user.email,
                "phone" : new_user.phone,
                "address" : new_user.address,
                "user_type" : new_user.user_type,
                "created_at" : new_user.created_at
            } 
        }), HTTP_201_CREATED

    # Error handling: to identify any errors that arises when creating a new user.
    except Exception as e:
        db.session.rollback() # Rollback removes uncommitted changes so that a new entry can be made.
        # Response of the error at hand.
        return jsonify({'Error':str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    

# User login based on their credentials (email and password).
@auth.post('/login')
def login():
     # This makes a request body containing the following (email and password), necessary in post man.
     email = request.json.get('email')
     password = request.json.get('password')

     try:
        if not password or not email:
            return jsonify({'Message':'Email and password required'}),HTTP_400_BAD_REQUEST
        
        user = User.query.filter_by(email=email).first()

        if user:# Password and email should both be cvalid or similar to what was stored.
            is_correct_password = bcrypt.check_password_hash(user.password, password)

            if is_correct_password:
                access_token = create_access_token(identity = user.id)
                refresh_token = create_refresh_token(identity=user.id)

                # returning the response
                return jsonify({
                    'User':{
                        'id':user.id,
                        'username':user.name,
                        'email':user.email,
                        'user_type':user.user_type,
                        'access_token':access_token,
                        'refresh_token':refresh_token
                    },
                    'Message':'You have successfully logged into your account.'
                }), HTTP_200_OK
            else:
                return jsonify({'Message':'Invalid Password'}), HTTP_401_UNAUTHORIZED


        else:
            return jsonify({'Message':'Invalid email address'}),HTTP_401_UNAUTHORIZED

     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR

# Refresh token a long lived credential used to obtain a new access token when the current one expires.
@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True) # When testing the end point, we have to always pass in a refresh token to get a new access token with the help of the user identity.
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token) # Response is to return the refresh token whenever we return the user.
