from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
from app.models.services import Service
from app.models.users import User
from app.models.gallery import Gallery
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# Services blueprint
services = Blueprint('services', __name__, url_prefix='/api/services')

# Create service
@services.route('/create', methods=['POST'])
@jwt_required()
def createService():
    data = request.json
    # Getting values from the incoming request.
    service_type = data.get('service_type')
    service_name = data.get('service_name')
    description = data.get('description')
    price_per_hour = data.get('price_per_hour')
    availability_status = data.get('availability_status')

    # Request body must include all the necessary attributes.
    if not service_type or not service_name or not description or not price_per_hour or not availability_status:
        return jsonify({'Error':'All fields are required'}),HTTP_400_BAD_REQUEST  # response returned in json format
    
    # Logic to create the service and only admins are allowed to do so.
    try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         if loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to create a service."}), HTTP_401_UNAUTHORIZED
         
         else:
              # Creating the service
              new_service = Service(
                   service_type = service_type,
                   service_name = service_name,
                   description = description,
                   price_per_hour = price_per_hour,
                   availability_status = availability_status
              )

              db.session.add(new_service)
              db.session.commit()

              return jsonify({'Message': 'Service created successfully',
                              'Service':{
                                   "id":new_service.id,
                                   "service_type":new_service.service_type,
                                   "service_name":new_service.service_name,
                                   "description":new_service.description,
                                   "price_per_hour":new_service.price_per_hour,
                                   "availability_status":new_service.availability_status,
                                   "created_at":new_service.created_at
                              }
              }), HTTP_201_CREATED

    except Exception as e:
         return jsonify({
              'Error':str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR
    
# Get all services
@services.get('/all')
@jwt_required()
def getAllServices():
     try:
         # json serialized variable
         all_services = Service.query.all()

         services_data = []

         #Looping through all the services in the database
         for service in all_services:
             service_info = {
                 "id":service.id,
                 "service_type":service.service_type,
                 "service_name":service.service_name,
                 "description":service.description,
                 "price_per_hour":service.price_per_hour,
                 "availability_status":service.availability_status,
                 "created_at":service.created_at
             }
             # Adding the service_info dictionary to the services_data list.
             services_data.append(service_info)

         return jsonify({
             'Message':'All services retrieved successfully',
             'Total_services':len(services_data),
             'Services': services_data 
           }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Retrieving a service by id.
@services.get('/<int:id>')
@jwt_required()
def getService(id):
      try:
           # Creating a serialized variable: one that can be easily converted to a json
           service = Service.query.filter_by(id=id).first()

           # For no service with that id
           if not service:
               return jsonify({"Error":"Service not found"}), HTTP_404_NOT_FOUND
      
           return jsonify({
               'Message': 'Service details retrieved successfully',
               'Service':{
                     "id":service.id,
                     "service_type":service.service_type,
                     "service_name":service.service_name,
                     "description":service.description,
                     "price_per_hour":service.price_per_hour,
                     "availability_status":service.availability_status,
                     "created_at":service.created_at
                 }
           }), HTTP_200_OK
      
      except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
      
# Updating a service's detail
@services.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateServiceDetails(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         # Checking for the given service id among services.
         service = Service.query.filter_by(id=id).first()

         if not service:
              return jsonify({"Error":"Service not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to create a service."}), HTTP_401_UNAUTHORIZED
         
         else:
              # Store info submitted when the request is made.
              service_type = request.get_json().get('service_type', service.service_type)
              service_name = request.get_json().get('service_name', service.service_name)
              description = request.get_json().get('description', service.description)
              price_per_hour = request.get_json().get('price_per_hour', service.price_per_hour)
              availability_status = request.get_json().get('availability_status', service.availability_status)

              # Variables defined in the request are stored
              service.service_type = service_type
              service.service_name = service_name
              service.description = description
              service.price_per_hour = price_per_hour
              service.availability_status = availability_status

              # Commiting changes to the db.
              db.session.commit()

              return jsonify({
                 'Message': 'Service details retrieved successfully',
                 'Service':{
                     "id":service.id,
                     "service_type":service.service_type,
                     "service_name":service.service_name,
                     "description":service.description,
                     "price_per_hour":service.price_per_hour,
                     "availability_status":service.availability_status,
                     "updated_at":service.updated_at
                 }
           }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Delete Service with its corresponding gallery.
@services.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteServiceDetails(id):
     try:
         #Getting the id of a currently logged in user, especially for cases where we have protected the route.
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         # Checking for the given service id among services.
         service = Service.query.filter_by(id=id).first()

         if not service:
              return jsonify({"Error":"Service not found"}), HTTP_404_NOT_FOUND
         
         elif loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to create a service."}), HTTP_401_UNAUTHORIZED
         
         else:
             # Corresponding gallery to be deleted.
             Gallery.query.filter_by(service_id=service.id).delete()

             # Deleting the service
             db.session.delete(service)
             db.session.commit()

             # Response after the service and it's corresponding gallery have been deleted.
             return jsonify({
                 'Message':service.name + "'s details and its associated gallery has been successfully deleted"
             }), HTTP_200_OK
         
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR
     
# Searching for a service
@services.get('/search')
@jwt_required()
def searchService():
     # request parameter storing the search term is created
     try:
          # Search query
           search_query = request.args.get('query', '') # Args are the query parameters in the url

           # Search for a service based on its name or it's type.
           services = Service.query.filter((Service.service_name.ilike(f"%search_query"))
                                            | (Service.service_type.ilike(f"%Search_query")) ).all()
           
           # When no results retrieved on searching.
           if len(services) == 0:
                 return jsonify({
                    'message':"No results found"
                 }), HTTP_404_NOT_FOUND
       
           else:
                
                services_data = []

                # Looping through all services in the db.
                for service in services:
                     service_info = {
                          "id":service.id,
                          "service_type":service.service_type,
                          "service_name":service.service_name,
                          "description":service.description,
                          "price_per_hour":service.price_per_hour,
                          "availability_status":service.availability_status,
                          "created_at":service.created_at 
                     }

                # Adding data to the service data
                services_data.append(service_info)

           return jsonify({
                'Message':'Customers with name {search_query} retrieved successfully',
                'Total_search results':len(services_data),
                'Customers_data': services_data
           }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR