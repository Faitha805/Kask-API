from flask import Blueprint, request, jsonify
from app.status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND
from app.models.users import User
from app.models.services import Service
from app.models.gallery import Gallery
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

# Gallery blueprint
galleries = Blueprint('galleries', __name__, url_prefix='/api/gallery')

# Create gallery
@galleries.route('/create', methods=['POST'])
@jwt_required()
def createGallery():
    data = request.get_json()
    # Getting values from the incoming request.
    image_url = data.get('image_url')
    caption = data.get('caption')
    service_name = data.get('service_name')

    # Request body must include the following
    if not image_url or not caption:
        return jsonify({'Error':'All fields are required'}), HTTP_400_BAD_REQUEST
    
    try:
         # ID of the currently logged in user
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         if loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to create a service."}), HTTP_401_UNAUTHORIZED
         
         # Retrieving the service to which the gallery belomngs based on the  name given
         service = Service.query.filter_by(service_name=service_name).first()
         
         if not service:
             return jsonify({'Error': 'Service not found'}), HTTP_400_BAD_REQUEST
         
         else:
              # Creating the gallery
              new_gallery = Gallery(
                   image_url=image_url,
                   caption=caption,
                   service_id=service.id
              )
              db.session.add(new_gallery)
              db.session.commit()

              return jsonify({'Message':'Gallery created successfully',
                              'Gallery':{
                                   "image_url":new_gallery.image_url,
                                   "caption":new_gallery.caption,
                                   "service_id":new_gallery.service_id,
                                   "created_at":new_gallery.created_at
                              }
              }),HTTP_201_CREATED
         
    except Exception as e:
         return jsonify({'Error':str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
# Get all galleries
@galleries.get('/all')
@jwt_required()
def getAllGalleries():
     try:
       # Creating a serialized variable: one that can be easily converted to a json
       all_galleries = Gallery.query.all()
       
       galleries_data = []

       # Looping through all galleries in the database.
       for gallery in all_galleries:
           gallery_info = {
               "image_url":gallery.image_url,
               "caption":gallery.caption,
               "service_id":gallery.service_id,
               "created_at":gallery.created_at
           }
           # Adding data to the gallery info dictionary
           galleries_data.append(gallery_info)

       return  jsonify({
           'Message':'All galleries retrieved successfully',
           'Total_galleries':len(galleries_data),
           'Galleries': galleries_data
       }), HTTP_200_OK
     
     except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR

# Get a gallery by id
@galleries.route('/<int:id>')
@jwt_required()
def getGallery(id):
    try:
         gallery = Gallery.query.filter_by(id=id).first

         # No gallery with this id
         if not gallery:
             return jsonify({'Error': 'Gallery not found'}), HTTP_400_BAD_REQUEST
    
         return jsonify({
             'Message':'Gallery details retrieved successfully',
             'Gallery':{
                     "image_url":gallery.image_url,
                     "caption":gallery.caption,
                     "service_id":gallery.service_id,
                     "created_at":gallery.created_at
             }
         }),HTTP_200_OK
         
    except Exception as e:
         return jsonify({'Error':str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
# Updating a gallery's details
@galleries.route('/edit/<int:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateGalleryDetails(id):
    try:
         # ID of the currently logged in user
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         gallery = Gallery.query.filter_by(id=id).first

         # No gallery with this id
         if not gallery:
             return jsonify({'Error': 'Gallery not found'}), HTTP_400_BAD_REQUEST
    
         elif loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to create a gallery."}), HTTP_401_UNAUTHORIZED
         
         else:
             # Store information submitted in the request body.
             image_url = request.get_json().get('image_url', gallery.image_url)
             caption = request.get_json().get('cation', gallery.caption)
             service_name = request.get_json().get('service_name', gallery.service_name)

             # Checking if a service with the given name exists.
             if service_name:
                 service = Service.query.filter_by(service_name=service_name).first()
             
             # return an error when the service does not exist.
             if not service:
                 return jsonify({'Eror':'Service not found.'}), HTTP_400_BAD_REQUEST
             
             # Give the gallery a new service id
             gallery.service_id = service.id

             # Update the gallery details.
             gallery.image_url = image_url
             gallery.caption = caption

             db.session.commit()

             return jsonify({
                 'Message':'Gallery updated successfully',
                 'Gallery': {
                     'id': gallery.id,
                     'image_url': gallery.image_url,
                     'caption':gallery.caption,
                     'service_name': gallery.service.service_name, # To retrieve the name of the service to which the gallery belongs
                     'updated_at':gallery.updated_at
                 }
             }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({'Error': str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
# Delete a gallery.
@galleries.route('/delete/<int:id>', methods = ['DELETE'])
@jwt_required()
def deleteGallery(id):
    try:
         # ID of the currently logged in user
         current_user = get_jwt_identity()

         # Variable to store the id itself
         loggedInUser = User.query.filter_by(id=current_user).first()

         gallery = Gallery.query.filter_by(id=id).first

         # No gallery with this id
         if not gallery:
             return jsonify({'Error': 'Gallery not found'}), HTTP_400_BAD_REQUEST
    
         elif loggedInUser.user_type != 'admin':
              return jsonify({"Error": "You are not authorised to create a gallery."}), HTTP_401_UNAUTHORIZED
         
         else:
             # Deleting the gallery
             db.session.delete(gallery)
             db.session.commit()

             # Response returned to the user
             return jsonify({
                 'Message':'Gallery has been deleted successfully.'
             }), HTTP_200_OK

    except Exception as e:
         return jsonify({
             'Error':str(e)
         }), HTTP_500_INTERNAL_SERVER_ERROR