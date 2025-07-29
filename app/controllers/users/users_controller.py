from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND
import validators
from app.models.users import User
from app.models.bookings import Booking
from app.extensions import db, bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

# Users blueprint
users = Blueprint('users', __name__, url_prefix='/api/users')

# Retrieving all users from the database
@users.get('/all')
@jwt_required() # To prevent unauthorized access
def getAllUsers():
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       all_users = User.query.all()
       
       users_data = []

       # Looping through all users in the database.
       for user in all_users:
           user_info = {
                'id':user.id,
                'username':user.name,
                'email':user.email,
                'phone':user.phone,
                'user_type':user.user_type,
                'created_at':user.created_at
           }
           # Adding data to that list, the user info dictionary.
           users_data.append(user_info)

       return jsonify({
           'Message':'All users retrieved successfully',
           'Total users':len(users_data),
           'Users': users_data
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR

# Getting all customers
@users.get('/customers')
@jwt_required()
def getAllCustomers():
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       all_customers = User.query.filter_by(user_type='customer').all()
       
       customers_data = []

       # Looping through all customers in the database.
       for customer in all_customers:
            customer_info = {
                'id':customer.id,
                'customername':customer.name,
                'email':customer.email,
                'phone':customer.phone,
                'address':customer.address,
                'created_at':customer.created_at,
                'bookings':[], # Retrieving the customers with their info on the bookings made.
            }

            # Checking if an attribute/ object has data
            if hasattr(customer, 'bookings'):
                customer_info['bookings']=[{
                    'id': booking.id,
                    'booking_status': booking.booking_status,
                    'amount': booking.amount,
                    'booking_date':booking.booking_date,
                    'start_time':booking.start_time,
                    'end_time':booking.end_time,
                    'user_id':booking.user_id,
                    'service_id':booking.service_id}
                    for booking in customer.bookings ]

            # Adding data to that list, the customer info dictionary.
            customers_data.append(customer_info)

       return jsonify({
           'Message':'All customers retrieved successfully',
           'Total customers':len(customers_data),
           'customers': customers_data
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Retrieving a user by id
@users.get('/user/<int:id>') # <int:id> simce the id attribute for the users was an integer and it was attributed as id.
@jwt_required()
def getUser(id):
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       user = User.query.filter_by(id=id).first()

       # For customers we return their bookings.
       bookings = []
       
       # Checking if an object has data for the defined attributes.
       if hasattr(user, 'bookings'):
           bookings =[{
                'id': booking.id,
                'booking_status': booking.booking_status,
                'amount': booking.amount,
                'booking_date':booking.booking_date,
                'start_time':booking.start_time,
                'end_time':booking.end_time,
                'user_id':booking.user_id,
                'service_id':booking.service_id}
                for booking in user.bookings ]
            
       return jsonify({
           'Message':'User retrieved successfully',
           'User':{
                'id':user.id,
                'username':user.name,
                'email':user.email,
                'phone':user.phone,
                'user_type':user.user_type,
                'created_at':user.created_at,
                'bookings':bookings
           }
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
    
# Update user details
@users.route('/edit/<int:id>', methods=['PUT', 'PATCH']) # PUT method is used to update all details of a particular resource, PATCH updates only a particular attribute or detail on a route.
@jwt_required()
def updateUserDetails(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         user = User.query.filter_by(id=id).first()

         # The id does not exist on the database
         if not user:
             return jsonify({"Error":"User not found"}), HTTP_404_NOT_FOUND
         
         # Only administrators can update user details and the id coming from the request must belong to the currently logged in use
         # Function to determine the type of the currenytly logged in user and to check if the id coming in from the request matches that of the user.
         elif loggedInUser.user_type != 'admin' and user.id != current_user:
             return jsonify({"Error":"You are not authorised to update the user details"}), HTTP_401_UNAUTHORIZED
         
         # For user type of 'admin' and/or the id of thr request matches the id of the currently logged in user.
         else:
             # Thus store info submitted when the request is made and submit it to the database.
             name = request.get_json().get('name', user.name)
             email = request.get_json().get('email', user.email)
             phone = request.get_json().get('phone', user.phone)
             address = request.get_json().get('address', user.address)
             user_type = request.get_json().get('user_type', user.user_type)

             # Making the password hashed
             if "password" in request.json:
                 hashed_password = bcrypt.generate_password_hash(request.json.get('password'))
                 user.password = hashed_password

             # Variables defined in the request are stored
             user.name = name
             user.email = email
             user.phone = phone
             user.address = address
             user.user_type = user_type

             # Committing the changes to the db.
             db.session.commit()

             # Returning a personalised response
             return jsonify({
                 'Message':name + "'s details have been successfully updated",
                 'User':{
                     'id':user.id,
                     'username':user.name,
                     'email':user.email,
                     'phone':user.phone,
                     'user_type':user.user_type,
                     'updated_at':user.updated_at
                 }
             }), HTTP_200_OK

     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Delete user details
@users.route('/delete/<int:id>', methods=['DELETE']) # PUT method is used to update all details of a particular resource, PATCH updates only a particular attribute or detail on a route.
@jwt_required() # End point protection.
def deleteUserDetails(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         # get user by id
         user = User.query.filter_by(id=id).first()

         # The id does not exist on the database
         if not user:
             return jsonify({"Error":"User not found"}), HTTP_404_NOT_FOUND
         
         # Only administrators can delete user details and the id coming from the request must belong to the currently logged in use
         # Function to determine the type of the currenytly logged in user and to check if the id coming in from the request matches that of the user.
         elif loggedInUser.user_type != 'admin' and user.id != current_user:
             return jsonify({"Error":"You are not authorised to delete the user details"}), HTTP_401_UNAUTHORIZED
         
         # For user type of 'admin' and/or the id of thr request matches the id of the currently logged in user.
         else:
             # Delete the user with his associated bookings.
             # For booking
             Booking.query.filter_by(user_id=user.id).delete()

             # Deleting the user
             db.session.delete(user)

             # Committing the changes to the db.
             db.session.commit()

             # Returning a personalised response
             return jsonify({
                 'Message':user.name + "'s details and associated books and payements have been successfully deleted"
             }), HTTP_200_OK

     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Searching for a customer
@users.get('/search')
@jwt_required()
def searchCustomers():
     # A request parameter storing a search term is necessary.
     try:
       # Search query
       search_query = request.args.get('query', '') # Args are the query parameters in the url

       # seaarch for users based on their name, ilike() makes the search case insensitive
       customers = User.query.filter((User.name.ilike(f"%{search_query}"))
                                     & (User.user_type.ilike('customer'))).all()
       
       # When no results are retrieved on searching.
       if len(customers) == 0:
           return jsonify({
               'message':"No results found"
           }), HTTP_404_NOT_FOUND
       
       else:
           
       
        customers_data = []

        # Looping through all customers in the database.
        for customer in customers:
            customer_info = {
                'id':customer.id,
                'customername':customer.name,
                'email':customer.email,
                'phone':customer.phone,
                'address':customer.address,
                'created_at':customer.created_at,
                'bookings':[] # Retrieving the customers with their info on the bookings made.
            }

            # Checking if an attribute/ object has data
            if hasattr(customer, 'bookings'):
                customer_info['bookings']=[{
                    'id': booking.id,
                    'booking_status': booking.booking_status,
                    'amount': booking.amount,
                    'booking_date':booking.booking_date,
                    'start_time':booking.start_time,
                    'end_time':booking.end_time,
                    'user_id':booking.user_id,
                    'service_id':booking.service_id}
                    for booking in customer.bookings ]
                
            # Adding data to that list, the customer info dictionary.
            customers_data.append(customer_info)

       return jsonify({
           'Message':'Customers with name {search_query} retrieved successfully',
           'Total_search results':len(customers_data),
           'Customers_data': customers_data
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR