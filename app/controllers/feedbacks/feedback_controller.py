from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
from app.models.feedback import Feedback
from app.models.users import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# Feedbacks blueprint
feedbacks = Blueprint('feedbacks', __name__, url_prefix='/api/feedbacks')

# Create a feedback
@feedbacks.route('/create', methods=['POST'])
@jwt_required()
def createFeedback():
    data = request.json
    # Getting values from the incoming request.
    name = data.get('name')
    phone_number = data.get('phone_number')
    email = data.get('email')
    message = data.get('message')

    if not name or not phone_number or not email or not message:
        return jsonify({'Error':'All fields are required'})
    
    try:
       new_feedback = Feedback(
           name = name,
           phone_number = phone_number,
           email = email,
           message = message
       )

       db.session.sdd(new_feedback)
       db.session.commit()

       return jsonify({'Message':'Feedback submitted successfully.',
                       'Feedback':{
                           "id":new_feedback.id,
                           "name":new_feedback.name,
                           "phone_number":new_feedback.phone_number,
                           "email":new_feedback.email,
                           "message":new_feedback.message,
                           "created_at":new_feedback.created_at
                       }}), HTTP_201_CREATED

    except Exception as e:
         return jsonify({
             'Error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Get all feedbacks
@feedbacks.get('/all')
@jwt_required()
def getAllFeedback():
    try:
        all_feedbacks = Feedback.query.all()

        feedbacks_data = []

        for feedback in all_feedbacks:
            feedback_info = {
                "id":feedback.id,
                "name":feedback.name,
                "phone_number":feedback.phone_number,
                "email":feedback.email,
                "message":feedback.message,
                "created_at":feedback.created_at
            }
            feedbacks_data.append(feedback_info)

        return jsonify({
            'Message':'All feedback retrieved successfully',
            'Total_feedback':len(feedbacks_data),
            'Feedbacks':feedbacks_data
        }), HTTP_200_OK

    except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
    
# Retrieving a feedback by id.
@feedbacks.get('/<int:id>')
@jwt_required()
def getFeedback(id):
      try:
           feedback = Feedback.query.filter_by(id=id).first()

           if not feedback:
               return jsonify({"Error":"Feedback not found"}), HTTP_404_NOT_FOUND
      
           return jsonify({
               'Message': 'Feedback details retrieved successfully',
               'Feedback':{
                      "id":feedback.id,
                      "name":feedback.name,
                      "phone_number":feedback.phone_number,
                      "email":feedback.email,
                      "message":feedback.message,
                      "created_at":feedback.created_at
                 }
           }), HTTP_200_OK
      
      except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR

# Functionality and backend logic to update a feedback will not be included because of no way to track the feedback by any one logged out customer.

# Deleting a feedback
@feedbacks.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteFeedbackDetails(id):
     try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         feedback = Feedback.query.filter_by(id=id).first()

         if not feedback:
            return jsonify({"Error":"Feedback not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin':
             return jsonify({"Error":"You are not authorised to delete the booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
             db.session.delete(feedback)
             db.session.commit()

             return jsonify({
                     'Message': 'Feedback successfully deleted'
             }), HTTP_200_OK
         
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
