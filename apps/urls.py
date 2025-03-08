from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('users/', views.users, name='users'),
    path('users/create/', views.create_user, name='create_user'), # Add create user urls
    path('users/update/<str:user_id>/', views.update_user, name='update_user'), # Add update user urls
    path('users/delete/<str:user_id>/', views.delete_user, name='delete_user'),
    
    path('favorites/', views.favorites, name='favorites'),

    path('cities/', views.cities, name='cities'),
    path('cities/create/', views.create_city, name='create_city'), # Add create city urls
    path('cities/update/<str:city_id>/', views.update_city, name='update_city'), # Add update city urls

    path('countries/', views.countries, name='countries'), # Add country urls
    path('countries/create/', views.create_country, name='create_country'), # Add create country urls
    path('countries/update/<str:country_id>/', views.update_country, name='update_country'), # Add update country urls

    path('upload/', views.upload, name='upload'),

    path('settings/', views.settings, name='settings'),

    path('banners/', views.banners, name='banners'),
    path('banners/create/', views.create_banner, name='create_banner'), # Add create banner urls
    path('delete_banner/<str:banner_id>/', views.delete_banner, name='delete_banner'),
    path('update_banner/<str:banner_id>/', views.update_banner, name='update_banner'),  # URL pattern for updating a banner

    path('reviews/', views.reviews, name='reviews'),
    path('reviews/create/', views.create_review, name='create_review'), # Add create review urls
    path('delete_review/<str:review_id>/', views.delete_review, name='delete_review'),

    path('places/', views.places, name='places'),
    path('places/create/', views.create_place, name='create_place'), # Add create place urls
    path('places/update/<str:place_id>/', views.update_place, name='update_place'), # Add update place urls
    path('places/view/<str:place_id>/', views.view_place, name='place_view'), # Add update place urls
    path('delete_place/<str:place_id>/', views.delete_place, name='delete_place'),
    path('places/<str:place_id>/delete-image/<path:image_url>/', views.delete_place_image, name='delete_place_image'),

    path('types/', views.types, name='types'),
    path('types/create/', views.create_type, name='create_type'), # Add create type urls
    path('types/update/<str:type_id>/', views.update_type, name='update_type'), # Add update type urls

    path('places_images/', views.places_images, name='places_images'), # Add places images urls
    path('places_images/create/', views.create_place_image, name='create_place_image'), # Add create places images urls
    path('places_images/update/<str:image_id>/', views.update_place_image, name='update_place_image'), # Add update places images urls
    
    path('services/', views.services, name='services'), # Add services urls
    path('services/create/', views.create_service, name='create_service'), # Add create services urls
    path('services/update/<str:service_id>/', views.update_service, name='update_service'), # Add update services urls
    path('delete_service/<str:service_id>/', views.delete_service, name='delete_service'),

    path('places_services/', views.places_services, name='places_services'), # Add places services urls
    path('places_services/create/', views.create_place_service, name='create_place_service'), # Add create places services urls
    path('places_services/update/<str:place_service_id>/', views.update_place_service, name='update_place_service'), # Add update places services urls

    path('pages-calendar/', views.pages_calendar, name='pages-calendar'),
    path('pages-pricing/', views.pages_pricing, name='pages-pricing'),
    path('pages-faqs/', views.pages_faqs, name='pages-faqs'),
    path('auth-lock-screen/', views.auth_lock_screen, name='auth-lock-screen'),
    path('auth-signin/', views.auth_signin, name='auth_signin'),
    path('logout/', views.auth_logout, name='auth_logout'),  # Add this line

    path('notification/', views.notification, name='notification'),

]