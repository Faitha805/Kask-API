from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND
from app.models.users import User
from app.models.bookings import Booking
from app.models.services import Service
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import and_, or_
from datetime import datetime, date

# Booking blueprint
bookings = Blueprint('bookings', __name__, url_prefix='/api/bookings')

# Create booking
@bookings.route('/create', methods=['POST'])
@jwt_required()
def createBooking():
    data = request.json
    # Getting values from the incoming request
    start_time_str = data.get('start_time') # Hour:Minute (24 hour clock system.)
    end_time_str = data.get('end_time')
    # total_unit_price = data.get('total_unit_price')
    booking_date_str = data.get('booking_date') 
    # booking_status = data.get('booking_status')
    service_name = data.get('service_name')

    # Request body must include the following.
    if not start_time_str or not end_time_str  or not booking_date or not service_name:
        return jsonify({'Error':'All fields are required'}),HTTP_400_BAD_REQUEST  # response returned in json format
    
    # Booking date should be in the future
    try:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
    # The string is in a wrong format i.e. not ISO date format.
    except ValueError:
         return jsonify({'Error': 'Invalid date format. Use ISO format (YYYY-MM-DD)'}), HTTP_400_BAD_REQUEST
    
    today = date.today()
    if booking_date < today:
        return jsonify({'Error':'Booking date cannot be in the past.'}), HTTP_400_BAD_REQUEST
    
     # Retrieve the service based on name given in request.
    service = Service.query.filter_by(service_name=service_name).first()
    if not service:
        return jsonify({'Error': 'Service not found'}), HTTP_400_BAD_REQUEST
    
    # Calculating the total unit price for the booked service
    try:
        # Converting start and endtime to  time objects for computation
        start_time = datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.strptime(end_time_str, '%H:%M').time()
    except ValueError:
        return jsonify({'Error':'Invalid time format. Use HH:MM'}), HTTP_400_BAD_REQUEST
    
    # Duration booked
    start = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)

    if end <= start:
        return jsonify({'End time must be after start time.'}), HTTP_400_BAD_REQUEST
    duration = (end - start).total_seconds() / 3600 # Converting seconds to hours

    total_unit_price = service.price_per_hour * duration

    # Check for overlapping bookings on the same date and overlapping times
    overlap = Booking.query.filter(
        Booking.booking_date == booking_date,
        or_(
            and_(Booking.start_time < end_time, Booking.end_time > start_time)
        )).first()

    if overlap:
        return jsonify({
            "Error": "The specified time overlaps with an existing booking."}), HTTP_409_CONFLICT

    # Logic that stores the new booking to the database.
    try:
        new_booking = Booking(
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            total_unit_price=total_unit_price,
            # booking_status=booking_status,
            user_id=get_jwt_identity(),
            service_id=service.id
        )
        db.session.add(new_booking)
        db.session.commit()
        
        return jsonify({'Message': 'Booking created successfully', 
                        'Booking':{
                         "id":new_booking.id,
                         "start_time":new_booking.start_time.strftime('%H:%M'), 
                         "end_time":new_booking.end_time.strftime('%H:%M'),
                         "total_unit_price":new_booking.total_unit_price,
                         "booking_status":new_booking.booking_status,
                         "user_id":new_booking.user_id,
                         "service_id":new_booking.service_id,
                         "created_at":new_booking.created_at
                        }
        }), HTTP_201_CREATED
    # The strftime() function or string format time is used to convert a datetime object into a string while 
    # the strptime() function or string parse time is used to convert a string of date and time into a datetime object using the given format, eg hours and minutes (%H:%M)
            
    # Error handling: to identify any errors that arises when creating a new user.
    except Exception as e:
        db.session.rollback() # Rollback removes uncommitted changes so that a new entry can be made.
        # Response of the error at hand.
        return jsonify({'Error':str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
# Get all bookings
@bookings.get('/all')
@jwt_required() # To prevent unauthorized access
def getAllBookings():
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
       
       bookings_data = []

       # Looping through all bookings in the database.
       for booking in all_bookings:
           booking_info = {
                 "id":booking.id,
                 "start_time":booking.start_time, 
                 "end_time":booking.end_time,
                 "total_unit_price":booking.total_unit_price,
                 "booking_status":booking.booking_status,
                 "user":{
                     'id':booking.user.id,
                     'username':booking.user.name,
                     'email':booking.user.email,
                     'phone':booking.user.phone,
                     'user_type':booking.user.user_type,
                     'created_at':booking.user.created_at
                 },
                 "service":{
                     'id':booking.service.id,
                     'service_type':booking.service.service_type,
                     'service_name':booking.service.service_name,
                     'description':booking.service.description,
                     'price_per_hour':booking.service.price_per_hour,
                     'availability_status':booking.service.availability_status,
                     'created_at':booking.service.created_at
                 },
                 "created_at":booking.created_at
           }
           # Adding data to that list, the booking info dictionary.
           bookings_data.append(booking_info)

       return jsonify({
           'Message':'All bookings retrieved successfully',
           'Total_bookings':len(bookings_data),
           'Bookings': bookings_data
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Get all bookings that belong to a particular user
@bookings.get('/user/<int:user_id>')
@jwt_required()
def getAllBookingsOfUser(user_id):
    try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         user = User.query.filter_by(id=id).first()

         if not user:
             return jsonify({"Error":"User not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin' and user.id != current_user:
             return jsonify({"Error":"You are not authorised to retrieve the user's booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
             user_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

             user_bookings_data = []

             for booking in user_bookings:
                 bookings_info={
                     "id":booking.id,
                     "start_time":booking.start_time, 
                     "end_time":booking.end_time,
                     "total_unit_price":booking.total_unit_price,
                     "booking_status":booking.booking_status,
                     "service":{
                                 'id':booking.service.id,
                                 'service_type':booking.service.service_type,
                                 'service_name':booking.service.service_name,
                                 'description':booking.service.description,
                                 'price_per_hour':booking.service.price_per_hour,
                                 'availability_status':booking.service.availability_status,
                                 'created_at':booking.service.created_at
                              },
                     "created_at":booking.created_at
                     }
             user_bookings_data.append(bookings_info)

             return jsonify({
                              'Message':'All bookings for user with id, ' + user_id + ' retrieved successfully',
                              'Total_bookings':len(user_bookings_data),
                              'Bookings': user_bookings_data
             }), HTTP_200_OK
     
    except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
    
# Retrieving a booking by id
@bookings.get('/<int:booking_id>') # <int:id> simce the id attribute for the bookings was an integer and it was attributed as id.
@jwt_required()
def getBooking(booking_id):
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       booking = Booking.query.filter_by(id=booking_id).first()

       # For no booking with that id
       if not booking:
           return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND

       return jsonify({
           'Message':'Booking details retrieved successfully',
           'Booking':{
                 "id":booking.id,
                 "start_time":booking.start_time, 
                 "end_time":booking.end_time,
                 "total_unit_price":booking.total_unit_price,
                 "booking_status":booking.booking_status,
                 "user":{
                     'id':booking.user.id,
                     'username':booking.user.name,
                     'email':booking.user.email,
                     'phone':booking.user.phone,
                     'user_type':booking.user.user_type,
                     'created_at':booking.user.created_at
                 },
                 "service":{
                     'id':booking.service.id,
                     'service_type':booking.service.service_type,
                     'service_name':booking.service.service_name,
                     'description':booking.service.description,
                     'price_per_hour':booking.service.price_per_hour,
                     'availability_status':booking.service.availability_status,
                     'created_at':booking.service.created_at
                 },
                 "created_at":booking.created_at
           }
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
    
# Updating a booking's detail
@bookings.route('/edit/<int:id>', methods=['PUT', 'PATCH']) # PUT method is used to update all details of a particular resource, PATCH updates only a particular attribute or detail on a route.
@jwt_required()
def updateBookingDetails(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         booking = Booking.query.filter_by(id=id).first()

         # The id does not exist on the database
         if not booking:
             return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND
         
         # Only administrators can update booking details and the id coming from the request must belong to the currently logged in use
         # Function to determine the type of the currenytly logged in user and to check if the id coming in from the request matches that of the user.
         elif loggedInUser.user_type != 'admin' and booking.user_id != current_user:
             return jsonify({"Error":"You are not authorised to update the booking details"}), HTTP_401_UNAUTHORIZED
         
         # For user type of 'admin' and/or the id of thr request matches the id of the currently logged in user.
         else:
             # Thus store info submitted when the request is made and submit it to the database.
             start_time = request.get_json().get('start_time', booking.start_time)
             end_time = request.get_json().get('end_time', booking.end_time)
            # total_unit_price = request.get_json().get('total_unit_price', booking.total_unit_price)
             booking_date = request.get_json().get('booking_date', booking.booking_date) # Year-Month-Day
             service_name = request.get_json().get('service_name', None)
             
         # Non-overlapping booking start and end time
        #  # Converting string date and times from the request to date/time objects.
        #  try:
        #     booking_date_obj = date.fromisoformat(booking_date) 
        #     start_time_obj = time.fromisoformat(start_time)
        #     end_time_obj = time.fromisoformat(end_time)

        #  # The string is in a wrong format i.e. not ISO date format.
        #  except ValueError:
        #     return jsonify({'Error': 'Invalid date or time format. Use ISO format (YYYY-MM-DD, HH:MM)'}), HTTP_400_BAD_REQUEST
    
         # Retrieve the service based on new service name given in request. (When service name is to be changed or updated.)
         if service_name:
            service = Service.query.filter_by(service_name=service_name).first()

         if not service:
            return jsonify({'Error': 'Service not found'}), HTTP_400_BAD_REQUEST
        
         booking.service_id = service.id # The new booking is given the new service id.

         # Check for overlapping bookings on the same date
         overlap = Booking.query.filter(
            Booking.booking_date == booking_date,
            or_(
                and_(Booking.start_time < end_time, Booking.end_time > start_time)
            ),
            Booking.id != id  # Exclude current booking from overlap check
        ).first()

         if overlap:
            return jsonify({"Error": "The specified time overlaps with an existing booking."}), HTTP_409_CONFLICT

        # Update booking fields
         booking.booking_date = booking_date
         booking.start_time = start_time
         booking.end_time = end_time
         # booking.total_unit_price = total_unit_price

         db.session.commit()

         return jsonify({
            'Message': 'Booking updated successfully',
            'Booking': {
                'id': booking.id,
                'booking_date': booking.booking_date,
                'start_time': booking.start_time,
                'end_time': booking.end_time,
                'total_unit_price': booking.total_unit_price,
                'booking_status': booking.booking_status,
                'updated_at':booking.updated_at
            }
        }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
     
# Update booking status
# 1. Cancel booking
@bookings.route('/<int:id>/cancel', methods=['PATCH']) # Cancel a booking using it's id.
@jwt_required()
def cancelBooking(id):
     try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         booking = Booking.query.filter_by(id=id).first()

         if not booking:
             return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin' and booking.user_id != current_user:
             return jsonify({"Error":"You are not authorised to update the booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
            # Current date
            date_now = datetime.today().date()

            # The time in days between cancel date and booking date
            delta_days = (booking.booking_date - date_now).days

            # To make sure that an already cancelled (in all case, upper or lower) booking cannot be recancelled
            if booking.booking_status.lower() == 'cancelled':
                return jsonify({'Error':'Booking already cancelled.'}), HTTP_400_BAD_REQUEST
            
            elif delta_days < 1:
                return jsonify({'Message': 'Booking cannot be cancelled less than 1 day before the booking date.'}), HTTP_400_BAD_REQUEST
            
            else:
                booking.booking_status = 'cancelled'
                db.session.commit()

            return jsonify({
                     'Message': 'Booking cancelled successfully',
                     'Booking': {
                        'id': booking.id,
                        'booking_date': booking.booking_date,
                        'start_time': booking.start_time,
                        'end_time': booking.end_time,
                        'total_unit_price': booking.total_unit_price,
                        'booking_status': booking.booking_status,
                        'cancelled_at':booking.updated_at
                     }
                     }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
     
# Undo booking cancellation
@bookings.route('/<int:id>/uncancel', methods=['PATCH']) # Uncancel a booking using it's id.
@jwt_required()
def uncancelBooking(id):
     try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         booking = Booking.query.filter_by(id=id).first()

         if not booking:
             return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin' and booking.user_id != current_user:
             return jsonify({"Error":"You are not authorised to update the booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
            # Current date
            date_now = datetime.today().date()

            # The time in days between cancel date and booking date
            delta_days = (booking.booking_date - date_now).days

            # A booking that is not already cancelled cannot be uncancelled.
            if booking.booking_status.lower() != 'cancelled':
                return jsonify({'Error':'Booking is not cancelled.'}), HTTP_400_BAD_REQUEST
            
            elif delta_days < 1:
                return jsonify({'Message': 'Booking cancellation cannot be undone less than 1 day before the booking date.'}), HTTP_400_BAD_REQUEST
            
            else:
                booking.booking_status = 'confirmed'
                db.session.commit()

            return jsonify({
                     'Message': 'Booking status reverted to confirmed successfully',
                     'Booking': {
                        'id': booking.id,
                        'booking_date': booking.booking_date,
                        'start_time': booking.start_time,
                        'end_time': booking.end_time,
                        'total_unit_price': booking.total_unit_price,
                        'booking_status': booking.booking_status,
                        'uncancelled_at':booking.updated_at
                     }
                     }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
     
# Complete booking
@bookings.route('/<int:id>/complete', methods=['PATCH']) # Mark a booking as completed using it's id.
@jwt_required()
def completeBooking(id):
     try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         booking = Booking.query.filter_by(id=id).first()

         if not booking:
             return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND
         
         # Users cannot mark a booking as completed
         elif loggedInUser.user_type != 'admin': 
             return jsonify({"Error":"You are not authorised to update the booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
            datetime_now = datetime.now()
            time_now = datetime_now.time()
            date_now = datetime_now.date()

            # To make sure that an already cancelled (in all case, upper or lower) booking cannot be marked as completed.
            if booking.booking_status.lower() == 'cancelled':
                return jsonify({'Error':'Cancelled booking cannot be marked as completed.'}), HTTP_400_BAD_REQUEST
            
            elif (booking.booking_date != date_now) and (time_now < booking.start_time):
                return jsonify({'Message': 'Booking cannot be completed before start time or on any day other than the booking date.'}), HTTP_400_BAD_REQUEST
            
            else:
                booking.booking_status = 'completed'
                db.session.commit()

            return jsonify({
                     'Message': 'Booking completed successfully',
                     'Booking': {
                        'id': booking.id,
                        'booking_date': booking.booking_date,
                        'start_time': booking.start_time,
                        'end_time': booking.end_time,
                        'total_unit_price': booking.total_unit_price,
                        'booking_status': booking.booking_status,
                        'completed_at':booking.updated_at
                     }
                     }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Mark booking as missed
@bookings.route('/<int:id>/missed', methods=['PATCH']) # Mark a booking as missed using it's id.
@jwt_required()
def missedBooking(id):
     try:
         current_user = get_jwt_identity()

         loggedInUser = User.query.filter_by(id=current_user).first()

         booking = Booking.query.filter_by(id=id).first()

         if not booking:
             return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND
         
         # Users cannot mark a booking as missed
         elif loggedInUser.user_type != 'admin': 
             return jsonify({"Error":"You are not authorised to update the booking details"}), HTTP_401_UNAUTHORIZED
         
         else:
            datetime_now = datetime.now()
            time_now = datetime_now.time()
            date_now = datetime_now.date()

            # To make sure that an already cancelled (in all case, upper or lower) booking cannot be marked as completed.
            if booking.booking_status.lower() in ['cancelled', 'completed']:
                return jsonify({'Error':'Booking already cancelled or completed.'}), HTTP_400_BAD_REQUEST
            
            # Booking date and/or end_time have not yet been reached.
            elif (booking.booking_date > date_now) or (booking.booking_date == date_now and time_now > booking.end_time):
                return jsonify({'Message': 'Booking cannot be marked as missed before end time or the booking date have been reached.'}), HTTP_400_BAD_REQUEST
            
            else:
                booking.booking_status = 'missed'
                db.session.commit()

            return jsonify({
                     'Message': 'Booking has been missed',
                     'Booking': {
                        'id': booking.id,
                        'booking_date': booking.booking_date,
                        'start_time': booking.start_time,
                        'end_time': booking.end_time,
                        'total_unit_price': booking.total_unit_price,
                        'booking_status': booking.booking_status,
                        'updated_at':booking.updated_at
                     }
                     }), HTTP_200_OK

     except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

# Deleting a booking.
@bookings.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required() # End point protection.
def deleteBooking(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         # get user by id
         booking = Booking.query.filter_by(id=id).first()

         # The id does not exist on the database
         if not booking:
             return jsonify({"Error":"Booking not found"}), HTTP_404_NOT_FOUND
         
         # Only administrators can delete user details and the id coming from the request must belong to the currently logged in use
         # Function to determine the type of the currenytly logged in user and to check if the id coming in from the request matches that of the user.
         elif loggedInUser.user_type != 'admin' and booking.user_id != current_user:
             return jsonify({"Error":"You are not authorised to delete the booking details"}), HTTP_401_UNAUTHORIZED
         
         # For user type of 'admin' and/or the id of the request matches the id of the currently logged in user.
         else:
             # Deleting the booking
             db.session.delete(booking)

             # Committing the changes to the db.
             db.session.commit()

             # Returning a personalised response
             return jsonify({
                 'Message':"Booking details have been successfully deleted"
             }), HTTP_200_OK

     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR