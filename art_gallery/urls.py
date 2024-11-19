from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # Login page
    path('register/', views.register_view, name='register'),  # Register page
    path('style-transfer/', views.upload_images, name='transfer_style'),
    path('3d-images/', views.three_d_images_page, name='three_d_images_page'),
    path('generate-3d-from-canvas/', views.generate_3d_from_canvas, name='generate_3d_from_canvas'),
    path('generate-3d/', views.generate_3d, name='generate_3d'),
    path('art-gallery/', views.art_gallery, name='art_gallery'),
    path('upload-art/', views.upload_art, name='upload_art'),
    path('', views.home, name='home'),
]
