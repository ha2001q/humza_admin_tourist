from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
import json
import random
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os
from django.conf import settings
from django.http import JsonResponse
from firebase_admin import credentials, initialize_app, storage, firestore, auth, messaging
import uuid  # To generate unique file names
from django.core.paginator import Paginator
from django.shortcuts import render
from .decorators import login_required  # Import the decorator
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
import openpyxl

import requests


db = firestore.client()
# bucket = storage.client()

@login_required
def index(request):
    # Fetch data from 'Banner_city' collection
    banner_city_ref = db.collection('Banner_city')
    docs = banner_city_ref.get()
    data = {}
    # Get All the documents data
    for doc in docs:
        data[doc.id] = doc.to_dict()

     # Initialize counts to zero
    new_users = 0
    new_reviews = 0
    new_places = 0
    total_cities = 0

    # Fetch the count from database
    users_ref = db.collection('Users').get()
    new_users = len(users_ref)
    reviews_ref = db.collection('User_comments').get()
    new_reviews = len(reviews_ref)
    places_ref = db.collection('Places').get()
    new_places = len(places_ref)
    cities_ref = db.collection('Citys').get()
    total_cities = len(cities_ref)



    context = {
        'banner_city_data': data,
          'new_users': new_users,
        'new_reviews': new_reviews,
        'new_places': new_places,
        'total_cities': total_cities,
    }
    return render(request, 'index.html', context)

@login_required
def banners(request):
    # Fetch all banner data from Firestore
    banner_ref = db.collection('Banners')
    banner_docs = banner_ref.get()
    banners_data = []

    # Fetch all cities and create a mapping using 'city_id' as the key
    city_ref = db.collection('Citys')
    city_docs = city_ref.get()
    cities = {city_doc.to_dict().get('city_id'): city_doc.to_dict().get('city_name', 'Unknown') for city_doc in city_docs}

    for banner_doc in banner_docs:
        banner_data = banner_doc.to_dict()

        # Get the city_id associated with the banner
        city_id = banner_data.get('city_id', 'Unknown')  # Default to 'Unknown' if city_id is not provided

        # Find the city_name using the city_id
        city_name = cities.get(str(city_id), "Unknown")  # Default to "Unknown" if city_id not found in mapping

        banners_data.append({
            'id': banner_doc.id,
            'data': banner_data,
            'city_name': city_name,
        })

    # Render the banners template with the compiled data
    return render(request, 'banners.html', {'banners_data': banners_data})

@login_required
def create_banner(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.POST.get('image')
        city_id = int(request.POST.get('city_id'))
        is_active = request.POST.get('is_active') == 'on'
        start_time = str(request.POST.get('start_time'))
        end_time = str(request.POST.get('end_time'))
        price=request.POST.get('price')
        time_created = str(datetime.now())
        # Create the new document and the corresponding data for that document
        doc_ref = db.collection('Banners').document()
        doc_ref.set({
            'title': title,
            'description': description,
            'image': image,
            'city_id': city_id,
            'is_active': is_active,
            'start_time': start_time,
            'end_time': end_time,
            'price':price,
            'time_created': time_created,
            'id': str(doc_ref.id)
        })
        return redirect('banners')

    # Fetch city options for dropdown
    citys_ref = db.collection('Citys')
    citys_docs = citys_ref.get()
    citys = []
    for doc in citys_docs:
        citys.append({'id': doc.to_dict().get('city_id'), 'name': doc.to_dict().get('city_name')})
     # Fetch types options for dropdown
    # types_ref = db.collection('Types')
    # types_docs = types_ref.get()
    # types = []
    # for doc in types_docs:
    #     types.append({'id': doc.id, 'name': doc.to_dict().get('name')})
    return render(request, 'create_banner.html', {'citys': citys, 'types': types})

@login_required
def delete_banner(request, banner_id):
    # Get the document reference for the banner to be deleted
    banner_ref = db.collection('Banners').document(banner_id)

    # Check if the banner exists
    if banner_ref.get().exists:
        # Delete the banner
        banner_ref.delete()
        # Redirect back to the banners page after deletion
        return redirect('banners')
    else:
        # If the banner doesn't exist, you can show an error or redirect elsewhere
        return render(request, 'not_found.html')  # Custom 404 page or message

@login_required
def update_banner(request, banner_id):
    # Fetch the existing banner data from Firestore
    banner_ref = db.collection('Banners').document(banner_id)
    banner_data = banner_ref.get()

    if not banner_data.exists:
        return render(request, 'not_found.html')  # Return not found if banner doesn't exist

    banner_data = banner_data.to_dict()

    if request.method == 'POST':
        # Get updated data from the form
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.POST.get('image')  # You might need to handle image uploads separately
        city_id = int(request.POST.get('city_id'))
        is_active = request.POST.get('is_active') == 'on'
        start_time = str(request.POST.get('start_time'))
        end_time = str(request.POST.get('end_time'))
        price = request.POST.get('price')
        time_created = str(datetime.now())

        # Update the existing banner document
        banner_ref.update({
            'title': title,
            'description': description,
            'image': image,  # You need to handle new image uploads if applicable
            'city_id': city_id,
            'is_active': is_active,
            'start_time': start_time,
            'end_time': end_time,
            'price': price,
            'time_created': time_created,
        })

        return redirect('banners')  # Redirect to banners list after updating

    # Fetch city options for the dropdown
    
    citys_ref = db.collection('Citys')
    citys_docs = citys_ref.get()
    citys = [{'id': doc.to_dict().get('city_id'), 'name': doc.to_dict().get('city_name')} for doc in citys_docs]

    return render(request, 'update_banner.html', {
        'banner': banner_data,  # Pass the existing banner data to the template
        'citys': citys,
    })


@login_required
def users(request):
    # Fetch user data from firebase
    users_ref = db.collection('Users')
    docs = users_ref.get()
    users_data = []
    for doc in docs:
        users_data.append({ 'id': doc.id, 'data': doc.to_dict() })
    return render(request, 'users.html', {'users_data': users_data})

@login_required
def create_user(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')
        user_image = request.FILES.get('user_image')  # Fetch the file
        user_created_at = str(datetime.now())

        # Upload image to Firebase Storage
        image_url = None
        if user_image:
            bucket = storage.bucket()
            file_name = f"Images/{uuid.uuid4()}-{user_image.name}"  # Unique file name
            blob = bucket.blob(file_name)
            blob.upload_from_file(user_image)
            blob.make_public()  # Make the file publicly accessible
            image_url = blob.public_url

        # Create the new document and the corresponding data for that document
        doc_ref = db.collection('Users').document()
        doc_ref.set({
            'user_name': user_name,
            'user_email': user_email,
            'user_password': user_password,
            'user_image': image_url,
            'user_created_at': user_created_at,
            'user_id': doc_ref.id
        })
        return redirect('users')

    return render(request, 'create_user.html')
 
@login_required
def update_user(request, user_id):
    # Fetch the user data to pre-fill the form
    user_data = db.collection('Users').document(user_id).get()
    if not user_data.exists:
        return render(request, '404.html', {'error': 'User not found'})

    user_data = user_data.to_dict()

    if request.method == 'POST':
        # Get user input from the form
        user_name = request.POST.get('user_name')
        user_email = request.POST.get('user_email')
        user_password = request.POST.get('user_password')
        user_image = request.FILES.get('user_image')  # Get the uploaded file

        # Prepare Firestore update data
        update_data = {
            'user_name': user_name,
            'user_email': user_email,
            'user_password': user_password,
        }

        # If a new image is uploaded, upload it to Firebase Storage
        if user_image:
            bucket = storage.bucket()
            blob = bucket.blob(f'Images/{user_image.name}')
            blob.upload_from_file(user_image, content_type=user_image.content_type)

            # Make the image publicly accessible
            blob.make_public()
            image_url = blob.public_url

            # Add the image URL to the update data
            update_data['user_image'] = image_url

        # Update the Firestore document
        db.collection('Users').document(user_id).update(update_data)

        return redirect('users')  # Redirect to the users list page

    return render(request, 'update_user.html', {
        'user_data': user_data,
        'user_id': user_id
    })

@login_required
def delete_user(request, user_id):
    try:
        # Get the user data by ID
        user_ref = db.collection('Users').document(user_id)
        user = user_ref.get()

        if not user.exists:
            return JsonResponse({'error': 'User not found'}, status=404)

        user_data = user.to_dict()
        user_image_url = user_data.get('user_image')
        auth_uid = user_data.get('auth_uid')  # Assuming the user's auth UID is stored in Firestore

        # Delete the user's image from Firebase Storage, if it exists
        if user_image_url and '/o/' in user_image_url:
            try:
                # Extract the file path from the image URL
                file_path = user_image_url.split('/o/')[1].split('?')[0]

                # Reference the file in Firebase Storage and delete it
                bucket.blob(file_path).delete()
            except Exception as e:
                print(f"Error deleting file: {e}")

        # Delete the user document from Firestore
        user_ref.delete()

        # Delete the user from Firebase Authentication
        if auth_uid:
            try:
                auth.delete_user(auth_uid)
            except Exception as e:
                print(f"Error deleting user from authentication: {e}")
                return JsonResponse({'error': 'Failed to delete user from authentication'}, status=500)

        return redirect('users')  # Redirect to the list of users after deletion

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def reviews(request):
    # Fetch user comments data from firebase
    reviews_ref = db.collection('User_comments')
    docs = reviews_ref.get()
    reviews_data = []
    for doc in docs:
        review_data = doc.to_dict()
        # Fetch User name
        user_id = review_data.get('user_id')
        # user_name = "Unknown"
        # if user_id:   
        #      user_ref = db.collection('Users').document(str(user_id)).get()
        #      if user_ref.exists:
        #          user_name = user_ref.to_dict().get('user_name', 'Unknown')

        # Fetch Place Name
        # place_id = review_data.get('place_id')
        # place_name = "Unknown"
        # if place_id:
        #    place_ref = db.collection('Places').document(str(place_id)).get()
        #    if place_ref.exists:
        #        place_name = place_ref.to_dict().get('name', 'Unknown')

        reviews_data.append({
            'id': doc.id,
            'data': review_data,
            
        })
    return render(request, 'reviews.html', {'reviews_data': reviews_data})

@login_required
def create_review(request):
    if request.method == 'POST':
           message = request.POST.get('message')
           place_id = int(request.POST.get('place_id'))
           rate = int(request.POST.get('rate'))
           user_id = int(request.POST.get('user_id'))
           user_image = request.POST.get('user_image')
           user_name = request.POST.get('user_name')
           timestamp = str(datetime.now())

        # Create the new document and the corresponding data for that document
           doc_ref = db.collection('User_comments').document()
           doc_ref.set({
               'message': message,
               'place_id': place_id,
               'rate': rate,
               'timestamp': timestamp,
               'user_id': user_id,
              'user_image': user_image,
              'user_name': user_name
           })
           return redirect('reviews')

    # Fetch city options for dropdown
    users_ref = db.collection('Users')
    users_docs = users_ref.get()
    users = []
    for doc in users_docs:
       users.append({'id': doc.id, 'name': doc.to_dict().get('user_name')})
    # Fetch types options for dropdown
    places_ref = db.collection('Places')
    places_docs = places_ref.get()
    places = []
    for doc in places_docs:
        places.append({'id': doc.id, 'name': doc.to_dict().get('name')})
    return render(request, 'create_review.html', {'users': users, 'places': places})

# def review_place_view(request, place_id):
#     place_ref = db.collection('Places').document(place_id).get()
#     if not place_ref.exists:
#         return render(request, 'not_found.html')

#     if request.method == 'POST':
#         # Fetch existing data
#         place_data = place_ref.to_dict()

#         # Retrieve updated form data
#         place_name = request.POST.get('place_name')
#         place_description = request.POST.get('place_description')
#         place_location = request.POST.get('place_location')
#         place_latitude = request.POST.get('Place_latitude')
#         place_longitude = request.POST.get('Place_longitude')
#         city_id = int(request.POST.get('city_id'))
#         type_id = int(request.POST.get('type_id'))
#         rate_avg = request.POST.get('rate_avg')
#         review_num =request.POST.get('review_num')

#         # Handle deleted images
#         deleted_images = json.loads(request.POST.get('deleted_images', '[]'))
#         place_images = place_data.get('place_image', [])
#         place_images = [img for img in place_images if img not in deleted_images]

#         # Handle newly added images
#         new_images = request.FILES.getlist('new_images')
#         for image in new_images:
#             # Upload new images to storage and get the URLs
#             bucket = storage.bucket()
#             blob = bucket.blob(f'places/{image.name}')
#             blob.upload_from_file(image)
#             blob.make_public()
#             place_images.append(blob.public_url)

#         # Update the document
#         doc_ref = db.collection('Places').document(place_id)
#         doc_ref.update({
#             'place_name': place_name,
#             'place_description': place_description,
#             'place_location': place_location,
#             'Place_latitude': place_latitude,
#             'Place_longitude': place_longitude,
#             'place_image': place_images,
#             'city_id': city_id,
#             'type_id': type_id,
#             'rate_avg': rate_avg,
#             'review_num': review_num,
#         })

#         return redirect('places')

#     # Fetch city options for dropdown
#     citys_ref = db.collection('Citys')
#     citys_docs = citys_ref.get()
#     citys = [{'id': doc.to_dict().get('city_id'), 'name': doc.to_dict().get('city_name')} for doc in citys_docs]

#     # Fetch types options for dropdown
#     types_ref = db.collection('Places_type')
#     types_docs = types_ref.get()
#     types = [{'id': doc.to_dict().get('type_id'), 'name': doc.to_dict().get('type_name')} for doc in types_docs]

#     return render(request, 'review_placeView.html', {
#         'place': place_ref.to_dict(),
#         'place_id': place_id,
#         'citys': citys,
#         'types': types,
#     })

@login_required
def delete_review(request, review_id):
    # Retrieve the review document using the provided review_id
    doc_ref = db.collection('User_comments').document(review_id)

    try:
        # Attempt to delete the review
        doc_ref.delete()
        print(f'Review {review_id} deleted successfully')
    except Exception as e:
        print(f'Error deleting review {review_id}: {e}')

    # Redirect back to the reviews page (or any other page you desire)
    return redirect('reviews')


@login_required
def places(request):
    # Fetch places data from Firebase
    places_ref = db.collection('Places')
    docs = places_ref.get()
    places_data = []
    for doc in docs:
        place_data = doc.to_dict()

        # Fetch City Name
        # city_id = place_data.get('city_id')
        # city_name = "Unknown"
        # if city_id:
        #     city_ref = db.collection('Citys').document(str(city_id)).get()
        #     if city_ref.exists:
        #         city_name = city_ref.to_dict().get('city_name', 'Unknown')

        # # Fetch Type Name
        # type_id = place_data.get('type_id')
        # type_name = "Unknown"
        # if type_id:
        #     type_ref = db.collection('Places_type').document(str(type_id)).get()
        #     if type_ref.exists:
        #         type_name = type_ref.to_dict().get('type_name', 'Unknown')

        places_data.append({
            'id': doc.id,
            'data': place_data,
            # 'city_name': city_name,
            # 'type_name': type_name,
        })

    # Paginate the data
    paginator = Paginator(places_data, 5)  # Show 10 places per page
    page_number = request.GET.get('page')
    places_page = paginator.get_page(page_number)

    return render(request, 'places.html', {'places_data': places_page})

@login_required
def create_place(request):
    if request.method == 'POST':
        place_name = request.POST.get('place_name')
        place_description = request.POST.get('place_description')
        place_location = request.POST.get('place_location')
        place_latitude = request.POST.get('place_latitude')
        place_longitude = request.POST.get('place_longitude')
        city_id = request.POST.get('city_id')
        type_id = request.POST.get('type_id')
        rate_avg = request.POST.get('rate_avg')
        review_num = request.POST.get('review_num')

        # Get all the uploaded images
        place_images = request.FILES.getlist('place_image')  # Handle multiple image uploads

        # Generate a unique random integer for place_id
        while True:
            place_id = random.randint(100000, 999999)  # Generate a random 6-digit number
            existing_place = db.collection('Places').where('place_id', '==', place_id).get()
            if not existing_place:  # Ensure the place_id is unique
                break

        image_urls = []  # List to hold image URLs

        # If images are uploaded, upload them to Firebase Storage
        for place_image in place_images:
            # Get the Firebase storage bucket
            bucket = storage.bucket()

            # Create a blob for the image with the original filename
            blob = bucket.blob(f'Images/{place_image.name}')

            # Upload the image to Firebase Storage
            blob.upload_from_file(place_image)

            # Make the file publicly accessible (optional)
            blob.make_public()

            # Get the public URL of the image and add it to the list
            image_urls.append(blob.public_url)

        # Create the new document and the corresponding data for that document
        doc_ref = db.collection('Places').document()
        doc_ref.set({
            'place_name': place_name,
            'place_description': place_description,
            'place_location': place_location,
            'Place_latitude': place_latitude,
            'Place_longitude': place_longitude,
            'place_image': image_urls,  # Store the list of image URLs
            'city_id': city_id,
            'type_id': type_id,
            'rate_avg': rate_avg,
            'review_num': review_num,
            'place_id': str(place_id)  # Use the unique random integer
        })

        return redirect('places')  # Redirect to places list after creation

    # Fetch city options for dropdown
    citys_ref = db.collection('Citys')
    citys_docs = citys_ref.get()
    citys = []
    for doc in citys_docs:
        citys.append({'id': str(doc.id), 'name': doc.to_dict().get('city_name')})

    # Fetch types options for dropdown
    types_ref = db.collection('Places_type')
    types_docs = types_ref.get()
    types = []
    for doc in types_docs:
        types.append({'id': str(doc.id), 'name': doc.to_dict().get('type_name')})

    return render(request, 'create_place.html', {'citys': citys, 'types': types})

@login_required
def update_place(request, place_id):
    place_ref = db.collection('Places').document(place_id).get()
    if not place_ref.exists:
        return render(request, 'not_found.html')

    if request.method == 'POST':
        # Fetch existing data
        place_data = place_ref.to_dict()

        # Retrieve updated form data
        place_name = request.POST.get('place_name')
        place_description = request.POST.get('place_description')
        place_location = request.POST.get('place_location')
        place_latitude = request.POST.get('Place_latitude')
        place_longitude = request.POST.get('Place_longitude')
        city_id = int(request.POST.get('city_id'))
        type_id = int(request.POST.get('type_id'))
        rate_avg = request.POST.get('rate_avg')
        review_num =request.POST.get('review_num')

        # Handle deleted images
        deleted_images = json.loads(request.POST.get('deleted_images', '[]'))
        place_images = place_data.get('place_image', [])
        place_images = [img for img in place_images if img not in deleted_images]

        # Handle newly added images
        new_images = request.FILES.getlist('new_images')
        for image in new_images:
            # Upload new images to storage and get the URLs
            bucket = storage.bucket()
            blob = bucket.blob(f'places/{image.name}')
            blob.upload_from_file(image)
            blob.make_public()
            place_images.append(blob.public_url)

        # Update the document
        doc_ref = db.collection('Places').document(place_id)
        doc_ref.update({
            'place_name': place_name,
            'place_description': place_description,
            'place_location': place_location,
            'Place_latitude': place_latitude,
            'Place_longitude': place_longitude,
            'place_image': place_images,
            'city_id': city_id,
            'type_id': type_id,
            'rate_avg': rate_avg,
            'review_num': review_num,
        })

        return redirect('places')

    # Fetch city options for dropdown
    citys_ref = db.collection('Citys')
    citys_docs = citys_ref.get()
    citys = [{'id': doc.to_dict().get('city_id'), 'name': doc.to_dict().get('city_name')} for doc in citys_docs]

    # Fetch types options for dropdown
    types_ref = db.collection('Places_type')
    types_docs = types_ref.get()
    types = [{'id': doc.to_dict().get('type_id'), 'name': doc.to_dict().get('type_name')} for doc in types_docs]

    return render(request, 'update_place.html', {
        'place': place_ref.to_dict(),
        'place_id': place_id,
        'citys': citys,
        'types': types,
    })

@login_required
def view_place(request, place_id):
    # Query the Places collection for documents where 'place_id' matches the given place_id
    place_ref = db.collection('Places').where('place_id', '==', place_id).get()

    if not place_ref:
        return render(request, 'not_found.html')

    # Since the query can return multiple documents, we'll use the first one (assuming 'place_id' is unique)
    place_data = place_ref[0].to_dict()  # Get the first document data

    if request.method == 'POST':
        # Retrieve updated form data
        place_name = request.POST.get('place_name')
        place_description = request.POST.get('place_description')
        place_location = request.POST.get('place_location')
        place_latitude = request.POST.get('Place_latitude')
        place_longitude = request.POST.get('Place_longitude')
        city_id = int(request.POST.get('city_id'))
        type_id = int(request.POST.get('type_id'))
        rate_avg = request.POST.get('rate_avg')
        review_num = request.POST.get('review_num')

        # Handle deleted images
        deleted_images = json.loads(request.POST.get('deleted_images', '[]'))
        place_images = place_data.get('place_image', [])
        place_images = [img for img in place_images if img not in deleted_images]

        # Handle newly added images
        new_images = request.FILES.getlist('new_images')
        for image in new_images:
            # Upload new images to storage and get the URLs
            bucket = storage.bucket()
            blob = bucket.blob(f'places/{image.name}')
            blob.upload_from_file(image)
            blob.make_public()
            place_images.append(blob.public_url)

        # Update the document using the document reference
        doc_ref = place_ref[0].reference  # Get the reference to the document
        doc_ref.update({
            'place_name': place_name,
            'place_description': place_description,
            'place_location': place_location,
            'Place_latitude': place_latitude,
            'Place_longitude': place_longitude,
            'place_image': place_images,
            'city_id': city_id,
            'type_id': type_id,
            'rate_avg': rate_avg,
            'review_num': review_num,
        })

        return redirect('places')

    # Fetch city options for dropdown
    citys_ref = db.collection('Citys')
    citys_docs = citys_ref.get()
    citys = [{'id': doc.to_dict().get('city_id'), 'name': doc.to_dict().get('city_name')} for doc in citys_docs]

    # Fetch types options for dropdown
    types_ref = db.collection('Places_type')
    types_docs = types_ref.get()
    types = [{'id': doc.to_dict().get('type_id'), 'name': doc.to_dict().get('type_name')} for doc in types_docs]

    return render(request, 'place_view.html', {
        'place': place_data,  # Pass the actual place data, not the query result
        'place_id': place_id,
        'citys': citys,
        'types': types,
    })

@login_required
def delete_place(request, place_id):
    try:
        # Get the place data by ID (assuming place_id is unique)
        place_ref = db.collection('Places').where('place_id', '==', place_id).limit(1).get()

        if not place_ref:
            return JsonResponse({'error': 'Place not found'}, status=404)

        place_doc = place_ref[0]
        place_data = place_doc.to_dict()
        place_image_urls = place_data.get('place_image', [])

        # Only attempt to delete images if place_image is a valid URL list
        if place_image_urls:
            # bucket = storage.client().get_bucket('yemen-tourist-guide.firebasestorage.app')  # Replace with your bucket name
            for image_url in place_image_urls:
                try:
                    # Extract the file path from the image URL
                    file_path = image_url.split('/o/')[1].split('?')[0]
                    
                    # Reference the file in Firebase Storage and delete it
                    bucket.blob(file_path).delete()
                except Exception as e:
                    # Handle cases where URL format is unexpected
                    print(f"Error deleting file: {e}")

        # Delete the place document from Firestore
        place_doc.reference.delete()

        return redirect('places')  # Redirect to the list of places after deletion
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def types(request):
    # Fetch places type data from firebase
    types_ref = db.collection('Places_type')
    docs = types_ref.get()
    types_data = []
    for doc in docs:
         types_data.append({ 'id': doc.id, 'data': doc.to_dict() })
    return render(request, 'types.html', {'types_data': types_data})

@login_required
def create_type(request):
    if request.method == 'POST':
        type_name = request.POST.get('type_name')
        type_icon = request.POST.get('type_icon')

        # Generate a unique random integer for type_id
        unique_type_id = random.randint(1000, 9999)  # You can adjust the range as needed

        # Create the new document and the corresponding data for that document
        doc_ref = db.collection('Places_type').document()
        doc_ref.set({
            'type_name': type_name,
            'type_icon': type_icon,
            'type_id': unique_type_id  # Set the random type_id here
        })

        return redirect('types')

    return render(request, 'create_type.html')

@login_required
def update_type(request, type_id):
    type_ref = db.collection('Places_type').document(type_id).get()
    if not type_ref.exists:
       return render(request, 'not_found.html')


    if request.method == 'POST':
         type_name = request.POST.get('type_name')
         type_icon = request.POST.get('type_icon')

        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Places_type').document(type_id)
         doc_ref.update({
             'type_name': type_name,
             'type_icon': type_icon
         })
         return redirect('types')
    return render(request, 'update_type.html', {'type': type_ref.to_dict(), 'type_id':type_id })

@login_required
def upload(request):
    if request.method == 'POST' and request.FILES.get('places_file'):
        places_file = request.FILES['places_file']

        try:
            # Check file type (Only allow .xlsx files)
            if not places_file.name.endswith('.xlsx'):
                return render(request, 'upload.html', {'error': 'Only .xlsx files are allowed'})

            # Save the uploaded file temporarily
            fs = FileSystemStorage()
            filename = fs.save(places_file.name, places_file)
            file_path = fs.path(filename)

            # Load the Excel file
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active  # Get the first sheet

            data_list = []

            # Read rows from Excel (assuming the first row is headers)
            headers = [cell.value for cell in sheet[1]]  # Extract headers from the first row

            for row in sheet.iter_rows(min_row=2, values_only=True):  # Start from second row
                place_data = dict(zip(headers, row))  # Map headers to row data
                if place_data:
                    place_data['place_id'] = str(random.randint(100000, 999999))  # Generate random 6-digit number
                    place_data['place_image'] = ['https://i.ytimg.com/vi/2w_lGtOhHUk/maxresdefault.jpg']
                    db.collection('Places').document().set(place_data)  # Save to Firestore
                    data_list.append(place_data)

        except Exception as e:
            print(f"Error processing file: {e}")
            return render(request, 'upload.html', {'error': f"Error processing file: {e}"})

        return render(request, 'upload.html', {'message': 'Places file uploaded successfully!'})

    return render(request, 'upload.html')

@login_required
def places_images(request):
     # Fetch places images data from firebase
    images_ref = db.collection('Places_images')
    docs = images_ref.get()
    images_data = []
    for doc in docs:
         images_data.append({ 'id': doc.id, 'data': doc.to_dict() })
    return render(request, 'places_images.html', {'images_data': images_data})

@login_required
def create_place_image(request):
    if request.method == 'POST':
         image = request.POST.get('image')
         place_id = request.POST.get('place_id')
        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Places_images').document()
         doc_ref.set({
            'image': image,
             'place_id': place_id,
            'image_id': doc_ref.id
         })
         return redirect('places_images')
    # Fetch all of the places to select from in the form
    places_ref = db.collection('Places')
    places_docs = places_ref.get()
    places = []
    for doc in places_docs:
       places.append({'id': doc.id, 'name': doc.to_dict().get('place_name')})
    return render(request, 'create_place_image.html', {'places': places})

@login_required
def update_place_image(request, image_id):
    image_ref = db.collection('Places_images').document(image_id).get()
    if not image_ref.exists:
       return render(request, 'not_found.html')
    if request.method == 'POST':
         image = request.POST.get('image')
         place_id = request.POST.get('place_id')
        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Places_images').document(image_id)
         doc_ref.update({
            'image': image,
              'place_id': place_id
         })
         return redirect('places_images')
       # Fetch all of the places to select from in the form
    places_ref = db.collection('Places')
    places_docs = places_ref.get()
    places = []
    for doc in places_docs:
       places.append({'id': doc.id, 'name': doc.to_dict().get('place_name')})

    return render(request, 'update_place_image.html', {'image': image_ref.to_dict(), 'image_id': image_id, 'places': places })

@login_required
def delete_place_image(request, place_id, image_url):
    # Get the reference to the place document
    place_ref = db.collection('Places').document(place_id)
    place = place_ref.get()
    
    if not place.exists:
        return JsonResponse({'success': False, 'message': 'Place not found'}, status=404)
    
    place_data = place.to_dict()
    place_images = place_data.get('place_image', [])

    # Check if the image URL exists in the place_images list
    if image_url not in place_images:
        return JsonResponse({'success': False, 'message': 'Image not found in place data'}, status=404)

    # Remove the image URL from the Firestore document
    place_images.remove(image_url)
    place_ref.update({'place_image': place_images})

    # Delete the image from Firebase Storage
    try:
        bucket = storage.bucket()
        blob_name = image_url.split('/o/')[1].split('?')[0]  # Extract the blob name from the URL
        blob_name = blob_name.replace('%2F', '/')  # Decode any encoded slashes
        blob = bucket.blob(blob_name)
        blob.delete()
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to delete image from storage: {str(e)}'}, status=500)

    return JsonResponse({'success': True, 'message': 'Image deleted successfully'})


@login_required
def services(request):
    # Fetch services data from Firestore
    services_ref = db.collection('Services')
    service_docs = services_ref.get()
    services_data = []

    # Fetch places from Firestore
    places_ref = db.collection('Places')
    places_docs = places_ref.get()

    # Create a dictionary of places using 'place_id' as the key
    places = {}
    for place_doc in places_docs:
        place_data = place_doc.to_dict()
        place_id = str(place_data.get('place_id'))  # Fetch 'place_id' from document data
        if place_id:  # Ensure the place_id exists
            places[place_id] = place_data.get('place_name')  # Map place_id to place_name

    # Process each service
    for service_doc in service_docs:
        service_data = service_doc.to_dict()
        place_id = str(service_data.get('place_id'))  # Get the place_id associated with the service

        # Find the place_name using the place_id
        place_name = places.get(place_id, "Unknown Place")  # Default to "Unknown Place" if not found

        services_data.append({
            'id': service_doc.id,
            'data': service_data,
            'place_name': place_name,
        })

    # Render the services template with the compiled data
    return render(request, 'services.html', {'services_data': services_data})

@login_required
def create_service(request):
    if request.method == 'POST':
        place_id = request.POST.get('place_id')
        service_name = request.POST.get('service_name')
        service_images = request.FILES.get('service_images')  # Get a single image
        service_location = request.POST.get('service_location')
        service_latitude = request.POST.get('service_latitude')
        service_longitude = request.POST.get('service_longitude')
        service_type = request.POST.get('service_type')

        image_url = None  # Variable to hold the image URL

        # If an image is uploaded, upload it to Firebase Storage
        if service_images:
            # Get the Firebase storage bucket
            bucket = storage.bucket()

            # Create a blob for the image with the original filename
            blob = bucket.blob(f'Images/{service_images.name}')

            # Upload the image to Firebase Storage
            blob.upload_from_file(service_images)

            # Make the file publicly accessible (optional)
            blob.make_public()

            # Get the public URL of the image
            image_url = blob.public_url

        # Create the new document and the corresponding data for that document
        doc_ref = db.collection('Services').document()
        doc_ref.set({
            'place_id': place_id,
            'service_name': service_name,
            'service_images': image_url,  # Store the single image URL
            'service_location': service_location,
            'service_latitude': service_latitude,
            'service_longitude': service_longitude,
            'service_type': service_type,
            'service_id': doc_ref.id
        })
        return redirect('services')

    # Fetch places from Firestore
    places_ref = db.collection('Places')
    places_docs = places_ref.get()

    places = []
    for doc in places_docs:
        places.append({'id': str(doc.to_dict().get('place_id')), 'name': doc.to_dict().get('place_name')})

    return render(request, 'create_service.html', {'places': places})

@login_required
def update_service(request, service_id):
    # Fetch the service document
    service_ref = db.collection('Services').document(service_id).get()
    if not service_ref.exists:
        return render(request, 'not_found.html')
    
    # Fetch places for the dropdown
    places_ref = db.collection('Places')
    places_docs = places_ref.get()

    # Create a list of places with id and name for the dropdown
    places = [{'id': str(doc.to_dict().get('place_id')), 'name': doc.to_dict().get('place_name')} for doc in places_docs]

    if request.method == 'POST':
        # Get form data
        place_id = request.POST.get('place_id')  # Add place_id from dropdown
        service_name = request.POST.get('service_name')
        service_images = request.POST.get('service_images')
        service_location = request.POST.get('service_location')
        service_latitude = request.POST.get('service_latitude')
        service_longitude = request.POST.get('service_longitude')
        service_type = request.POST.get('service_type')

        # Update the service document
        doc_ref = db.collection('Services').document(service_id)
        doc_ref.update({
            'place_id': place_id,  # Update place_id
            'service_name': service_name,
            'service_images': service_images,
            'service_location': service_location,
            'service_latitude': service_latitude,
            'service_longitude': service_longitude,
            'service_type': service_type,
        })
        return redirect('services')

    # Render the update form with service data and places for the dropdown
    return render(request, 'update_service.html', {
        'service': service_ref.to_dict(),
        'places': places,
    })

@login_required
def delete_service(request, service_id):
    # Get the service document by the provided service_id
    doc_ref = db.collection('Services').document(service_id)

    try:
        # Attempt to delete the service document
        doc_ref.delete()
        print(f'Service {service_id} deleted successfully')
    except Exception as e:
        print(f'Error deleting service {service_id}: {e}')

    # Redirect back to the services page
    return redirect('services')


@login_required
def places_services(request):
    # Fetch places services data from firebase
    places_services_ref = db.collection('Places_services')
    docs = places_services_ref.get()
    places_services_data = []
    for doc in docs:
         place_service_data = doc.to_dict()

          # Fetch Place Name
         place_id = place_service_data.get('place_id')
         place_name = "Unknown"  # Default value
         if place_id:
             place_ref = db.collection('Places').document(str(place_id)).get()
             if place_ref.exists:
                 place_name = place_ref.to_dict().get('place_name', "Unknown")

        # Fetch Service name
         service_id = place_service_data.get('service_id')
         service_name = "Unknown"  # Default value
         if service_id:
             service_ref = db.collection('Services').document(str(service_id)).get()
             if service_ref.exists:
                 service_name = service_ref.to_dict().get('service_name', "Unknown")

         places_services_data.append({
            'id': doc.id,
            'data': place_service_data,
             'place_name': place_name,
              'service_name': service_name,
        })

    return render(request, 'places_services.html', {'places_services_data': places_services_data})

@login_required
def create_place_service(request):
    if request.method == 'POST':
         place_id = int(request.POST.get('place_id'))
         service_id = int(request.POST.get('service_id'))

        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Places_services').document()
         doc_ref.set({
            'place_id': place_id,
             'service_id': service_id
         })
         return redirect('places_services')
   # Fetch all of the places to select from in the form
    places_ref = db.collection('Places')
    places_docs = places_ref.get()
    places = []
    for doc in places_docs:
        places.append({'id': doc.id, 'name': doc.to_dict().get('place_name')})

    # Fetch all of the services to select from in the form
    services_ref = db.collection('Services')
    services_docs = services_ref.get()
    services = []
    for doc in services_docs:
        services.append({'id': doc.id, 'name': doc.to_dict().get('service_name')})
    return render(request, 'create_place_service.html', {'places': places, 'services': services })

@login_required
def update_place_service(request, place_service_id):
    place_service_ref = db.collection('Places_services').document(place_service_id).get()
    if not place_service_ref.exists:
       return render(request, 'not_found.html')

    if request.method == 'POST':
         place_id = int(request.POST.get('place_id'))
         service_id = int(request.POST.get('service_id'))

        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Places_services').document(place_service_id)
         doc_ref.update({
            'place_id': place_id,
             'service_id': service_id
         })
         return redirect('places_services')
 # Fetch all of the places to select from in the form
    places_ref = db.collection('Places')
    places_docs = places_ref.get()
    places = []
    for doc in places_docs:
        places.append({'id': doc.id, 'name': doc.to_dict().get('place_name')})
  # Fetch all of the services to select from in the form
    services_ref = db.collection('Services')
    services_docs = services_ref.get()
    services = []
    for doc in services_docs:
       services.append({'id': doc.id, 'name': doc.to_dict().get('service_name')})
    return render(request, 'update_place_service.html', {'place_service': place_service_ref.to_dict(), 'place_service_id': place_service_id, 'places': places, 'services': services })


@login_required
def favorites(request):
    # Fetch user favorites data from firebase
    favorites_ref = db.collection('User_favorites')
    docs = favorites_ref.get()
    favorites_data = []
    for doc in docs:
         favorite_data = doc.to_dict()
         # Fetch Place Name
         place_id = favorite_data.get('place_id')
         place_name = "Unknown"  # Default value
        #  if place_id:
        #      place_ref = db.collection('Places').where('place_id', '==', str(place_id)).get()
        #      if place_ref:
        #         place = place_ref[0]
        #         place_data = place.to_dict()  # Convert to dictionary

        #         # Get user_name (if exists) or set to "Unknown"
        #         place_name = place_data.get('place_name', "Unknown")
        # Fetch User name
         user_id = favorite_data.get('user_id')
         user_name = "Unknown"  # Default value
         if user_id:
            #  Query Firestore to find the user
            user_ref = db.collection('Users').where('user_id', '==', str(user_id)).get()

            # Check if any user document is found
            if user_ref:
                # Assuming user_id is unique, we can take the first document
                user_doc = user_ref[0]  # Get the first document
                user_data = user_doc.to_dict()  # Convert to dictionary

                # Get user_name (if exists) or set to "Unknown"
                user_name = user_data.get('user_name', "Unknown")
            else:
                # If no user is found
                user_name = "Unknown"


         favorites_data.append({
            'id': doc.id,
            'data': favorite_data,
            #  'place_name': place_name,
            'user_name': user_name,
        })
         
    return render(request, 'favorite.html', {'favorites_data': favorites_data})



@login_required
def cities(request):
    # Fetch cities data from firebase
    cities_ref = db.collection('Citys')
    docs = cities_ref.get()
    cities_data = []
    for doc in docs:
         city_data = doc.to_dict()
         country_id = city_data.get('country_id')
         country_name = 'Unkown'
         if country_id:
           country_ref = db.collection('Countries').document(str(country_id)).get()
           if country_ref.exists:
                country_name = country_ref.to_dict().get('country_name', "Unknown")
         cities_data.append({'id': doc.id, 'data': city_data, 'country_name': country_name})
    return render(request, 'cities.html', {'cities_data': cities_data})

@login_required
def create_city(request):
    if request.method == 'POST':
          city_name = request.POST.get('city_name')
          country_id = request.POST.get('country_id')

        # Create the new document and the corresponding data for that document
          doc_ref = db.collection('Citys').document()
          doc_ref.set({
             'city_name': city_name,
            'country_id': country_id,
             'city_id': doc_ref.id
         })
          return redirect('cities')

    countries_ref = db.collection('Countries')
    countries_docs = countries_ref.get()
    countries = []
    for doc in countries_docs:
        countries.append({'id': doc.id, 'name': doc.to_dict().get('country_name')})
    return render(request, 'create_city.html', {'countries': countries})

@login_required
def update_city(request, city_id):
    city_ref = db.collection('Citys').document(city_id).get()
    if not city_ref.exists:
        return render(request, 'not_found.html')

    if request.method == 'POST':
          city_name = request.POST.get('city_name')
          country_id = request.POST.get('country_id')

        # Create the new document and the corresponding data for that document
          doc_ref = db.collection('Citys').document(city_id)
          doc_ref.update({
              'city_name': city_name,
            'country_id': country_id,
         })
          return redirect('cities')
     # Fetch types options for dropdown
    countries_ref = db.collection('Countries')
    countries_docs = countries_ref.get()
    countries = []
    for doc in countries_docs:
       countries.append({'id': doc.id, 'name': doc.to_dict().get('country_name')})
    return render(request, 'update_city.html', {'city': city_ref.to_dict(),'city_id': city_id, 'countries': countries})


@login_required
def countries(request):
    # Fetch countries data from firebase
    countries_ref = db.collection('Countries')
    docs = countries_ref.get()
    countries_data = []
    for doc in docs:
         countries_data.append({ 'id': doc.id, 'data': doc.to_dict() })
    return render(request, 'countries.html', {'countries_data': countries_data})

@login_required
def create_country(request):
    if request.method == 'POST':
         country_name = request.POST.get('country_name')
        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Countries').document()
         doc_ref.set({
            'country_name': country_name,
             'country_id': doc_ref.id
         })
         return redirect('countries')
    return render(request, 'create_country.html')

@login_required
def update_country(request, country_id):
    country_ref = db.collection('Countries').document(country_id).get()
    if not country_ref.exists:
        return render(request, 'not_found.html')

    if request.method == 'POST':
         country_name = request.POST.get('country_name')
        # Create the new document and the corresponding data for that document
         doc_ref = db.collection('Countries').document(country_id)
         doc_ref.update({
            'country_name': country_name
         })
         return redirect('countries')

    return render(request, 'update_country.html', {'country': country_ref.to_dict(),'country_id': country_id })


@login_required
def settings(request):
    return render(request, 'settings.html')

@login_required
def pages_calendar(request):
    return render(request, 'pages-calendar.html')

@login_required
def pages_pricing(request):
    return render(request, 'pages-pricing.html')

@login_required
def pages_faqs(request):
    return render(request, 'pages-faqs.html')

@login_required
def auth_lock_screen(request):
     return render(request, 'auth-lock-screen.html')

def auth_signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Query Firestore for the user with matching email
        users_ref = db.collection("User_admin").where("user_email", "==", email).stream()

        user_data = None
        for doc in users_ref:
            user_data = doc.to_dict()
            break  # Get the first matching document

        # Check if user exists and password matches
        if user_data and user_data.get("user_password") == password:
            request.session["admin_username"] = user_data["user_email"]  # Store session
            request.session["admin_image"] = user_data["user_image"]  # Store session
            messages.success(request, "Login successful!")
            return redirect("index")  # Redirect to the homepage (dashboard)
        else:
            messages.error(request, "Invalid email or password.")  # Show error message

    return render(request, "auth-signin.html")  # Reload login page on failure

def auth_logout(request):

    # Clear the session to log the user out
    request.session.flush()  # This clears all session data
    messages.success(request, "You have been logged out successfully.")
    return redirect("auth_signin")  # Redirect to login page

def get_all_tokens():
    # Fetch all documents in the 'Users' collection
    users_ref = db.collection('Users')
    docs = users_ref.stream()

    tokens = []
    for doc in docs:
        user_token = doc.to_dict().get('user_token')
        if user_token:
            tokens.append(user_token)
    
    return tokens

def notification(request):
    if request.method == "POST":
        title = request.POST.get("title")
        body = request.POST.get("body")

        # Get all tokens from the Users collection
        tokens = get_all_tokens()
        print(tokens)

        if not tokens:
            return JsonResponse({"error": "No tokens found in the Users collection"}, status=400)

        # Firebase API URL
        url = "https://fcm.googleapis.com/fcm/send"

        # Request headers
        headers = {
            "Authorization": f"key=BOJ47eXSYpTD7QYKC70YKrxOflaIccBoFqO_g1PxT8oKGUiVvNyZSkeJB0J6JJPYlDAChkzUIRqFl171fx4nb3wBOJ47eXSYpTD7QYKC70YKrxOflaIccBoFqO_g1PxT8oKGUiVvNyZSkeJB0J6JJPYlDAChkzUIRqFl171fx4nb3w",
            "Content-Type": "application/json"
        }

        # Payload for Firebase
        payload = {
            "registration_ids": tokens,  # Send to all retrieved tokens
            "notification": {
                "title": title,
                "body": body
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return JsonResponse({"message": "Notification sent", "response": response.json()})
            else:
                return JsonResponse({"error": response.text}, status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "Notification.html")
