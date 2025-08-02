from flask import Blueprint, request, jsonify
from flask_mail import Message as MailMessage
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
from app.models.users import User
from app.models.messages import Message
from app.models.bookings import Booking
from app.extensions import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

# Messages blueprint
messages = Blueprint('messages', __name__, url_prefix='/api/messages')

# Create/ send a message
@messages.route('/send', methods=['POST'])
@jwt_required()
def createMessage():
    data = request.json
    sender_id = get_jwt_identity()
    recipient_id = data.get('recipient_id')
    content = data.get('content')

    if not recipient_id:
        return jsonify({'Error':"Please enter the recipient's id."}), HTTP_400_BAD_REQUEST
    
    recipient = User.query.filter_by(id=recipient_id).first()
    if not recipient:
         return jsonify({'Error':'recipient not found, invalid recipient id.'}), HTTP_404_NOT_FOUND
    
    if not content:
        return jsonify({'Error':'Message content not given.'}), HTTP_400_BAD_REQUEST
    
    try:
 
        loggedInUser = User.query.filter_by(id=sender_id).first()

        if loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to send this message."}), HTTP_401_UNAUTHORIZED
         
        else:
              # Creating the message
              new_message = Message(
                   recipient_id = recipient_id,
                   content = content
              )

              db.session.add(new_message)
              db.session.commit()

        # Sending an email notificaation to users who prefer email messages (if email preference set to true, email will be sent)
        if recipient.email_preferences:
             # Email compostion and sending.
             email_subject = "New message from Kasokoso Beach"
             email_body = f"Your message is:{content}"

             try:
                  msg = MailMessage(
                       subject=email_subject,
                       recipients=[recipient.email],
                       body=email_body
                  )
                  
                  from app.__init__ import mail
                  mail.send(msg)

             except Exception as e:
                 db.session.rollback()
                 return jsonify({'Error':str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


        return jsonify({'Notification': 'Message sent successfully',
                              'Message':{
                                   "id":new_message.id,
                                   "sender_id":new_message.sender_id,
                                   "recipient_id":new_message.recipient_id,
                                   "content":new_message.content,
                                   "created_at":new_message.time_stamp
                              }
              }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({'Error':str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
# Messages for user booking history
@messages.get('/user/<int:user_id>/booking_messages')
@jwt_required()
def getBookingMessages(user_id):
  try:
     bookings = Booking.query.filter_by(id=user_id).order_by(Booking.booking_date.desc()).all()

     bookings_history = []

     now = datetime.now()

     for booking in bookings:
          if booking.booking_status.lower() == 'cancelled':
               message = f"Cancelled booking on {booking.booking_date.strftime('%Y-%m-%d')} for {booking.start_time.strftime('%H:%M')}"

          if booking.booking_status.lower() == 'missed':
               message = f"Missed booking on {booking.booking_date.strftime('%Y-%m-%d')} for {booking.start_time.strftime('%H:%M')}"

          if booking.booking_status.lower() == 'completed':
               message = f"Completed booking on {booking.booking_date.strftime('%Y-%m-%d')} for {booking.start_time.strftime('%H:%M')}"

          if booking.booking_status.lower() == 'confirmed':
               # Check if a booking is upcoming.
               booking_time = datetime.combine(booking.booking_date, booking.booking.start_time)
               if booking_time > now: # For booking time which has not yet reached.
                    message = f"Upcoming booking on {booking.booking_date.strftime('%Y-%m-%d')} for {booking.start_time.strftime('%H:%M')}"
               else: # For booking time which has passed but booking not yet marked complete
                    message = f"Pending booking on {booking.booking_date.strftime('%Y-%m-%d')} for {booking.start_time.strftime('%H:%M')}"
          else:
               # For available booking whose status is not cancelled, missed, completed or confirmed.
               message = f"Booking on {booking.booking_date.strftime('%Y-%m-%d')} at {booking.start_time.strftime('%H:%M')} with ststus: {booking.booking_status}."

          bookings_history.append(message)

     return jsonify (bookings_history)
  
  except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Read all user messages
@messages.get('/inbox/<int:user_id>')
@jwt_required()
def getAllUserMessages(user_id):
    try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         user = User.query.filter_by(id=id).first()

         if not user:
             return jsonify({"Error":"User not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin' and user.id != current_user:
             return jsonify({"Error":"You are not authorised to retrieve the user's booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
             user_messages = Message.query.filter_by(recipient_id=user_id).order_by(Message.timestamp.desc()).all()

             user_messages_data = []

             for message in user_messages:
                 messages_info={
                     "id":message.id,
                     "sender_id":message.sender_id, 
                     "recipient_id":message.recipient_id,
                     "content":message.content,
                     "timestamp":message.timestamp
                     }
             user_messages_data.append(messages_info)

             return jsonify({
                              'Message':'All messages retrieved successfully',
                              'Total_messages':len(user_messages_data),
                              'Messages': user_messages_data
             }), HTTP_200_OK
     
    except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
 
# Read a message by id (These are the messages sent to the user by admin and are not the booking history messages.)
@messages.get('/<int:id>') # <int:id> since the id attribute for the bookings was an integer and it was attributed as id.
@jwt_required()
def getMessage(id):
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       message = Message.query.filter_by(id=id).first()

       # For no booking with that id
       if not message:
           return jsonify({"Error":"Message not found"}), HTTP_404_NOT_FOUND

       return jsonify({
           'Notification':'Message details retrieved successfully',
           'Message':{
                 "id":message.id,
                 "sender_id":message.sender_id, 
                 "recipient_id":message.recipient_id,
                 "content":message.content,
                 "timestamp":message.timestamp
           }
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR

# Update or edit a message (functionality for the sender).
@messages.route('/edit/<int:id>', methods=['PUT', 'PATCH']) # PUT method is used to update all details of a particular resource, PATCH updates only a particular attribute or detail on a route.
@jwt_required()
def updateMessages(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         message = Message.query.filter_by(id=id).first()

         # The id does not exist on the database
         if not message:
             return jsonify({"Error":"Message not found"}), HTTP_404_NOT_FOUND
         
         # Only administrators can update booking details and the id coming from the request must belong to the currently logged in use
         # Function to determine the type of the currenytly logged in user and to check if the id coming in from the request matches that of the user.
         elif loggedInUser.user_type != 'admin' and message.sender_id != current_user:
             return jsonify({"Error":"You are not authorised to update the message details"}), HTTP_401_UNAUTHORIZED
         
         # For user type of 'admin' and/or the id of thr request matches the id of the currently logged in user.
         else:
            recipient_id = request.get_json().get('recipient_id', message.recipient_id)
            content = request.get_json().get('content', message.content)

            message.reecipient_id = recipient_id
            message.content = content

            db.session.commit()

         return jsonify({
            'Notification':'Message details updated successfully',
            'Message':{
                 "id":message.id,
                 "sender_id":message.sender_id, 
                 "recipient_id":message.recipient_id,
                 "content":message.content,
                 "timestamp":message.timestamp
            }
        }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
 
# delete a message(By Admin)
@messages.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteMessage(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         message = Message.query.filter_by(id=id).first()

         # The id does not exist on the database
         if not message:
             return jsonify({"Error":"Message not found"}), HTTP_404_NOT_FOUND
         
         # Only administrators can update booking details and the id coming from the request must belong to the currently logged in use
         # Function to determine the type of the currenytly logged in user and to check if the id coming in from the request matches that of the user.
         elif loggedInUser.user_type != 'admin':
             return jsonify({"Error":"You are not authorised to delete the message details"}), HTTP_401_UNAUTHORIZED
         
         # For user type of 'admin'.
         else:
            db.session.delete(message)

            db.session.commit()

         return jsonify({
            'Notification':'Message details deleted successfully'
        }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
 