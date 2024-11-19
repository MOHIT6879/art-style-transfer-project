from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
import tensorflow as tf
import os
from django.http import JsonResponse
import base64
from .models import Artwork
from django.core.files.storage import FileSystemStorage

MODEL_PATH = os.path.join('model')  
model = tf.saved_model.load(MODEL_PATH)

def tensor_to_image(tensor):
    tensor = tf.squeeze(tensor)  
    tensor = tf.clip_by_value(tensor, 0, 1) * 255  
    tensor = tf.cast(tensor, tf.uint8)  
    array = tensor.numpy()
    if array.ndim == 4: 
        array = array[0]
    return Image.fromarray(array)


def save_image_to_response(pil_image):
    image_io = BytesIO()
    pil_image.save(image_io, format='PNG')
    image_io.seek(0)
    return ContentFile(image_io.read(), name="styled_image.png")

# The main view to handle image uploads and style transfer
# def upload_images(request):
#     if request.method == 'POST':
#         # Get the uploaded files from the form
#         original_image_file = request.FILES.get('original_image')
#         style_image_file = request.FILES.get('style_image')

#         if original_image_file and style_image_file:
#             # Open the uploaded images with PIL
#             original_image = Image.open(original_image_file).convert('RGB')
#             style_image = Image.open(style_image_file).convert('RGB')

#             # Resize images to model's expected input size (adjust as necessary)
#             target_size = (256, 256)
#             original_image = original_image.resize(target_size)
#             style_image = style_image.resize(target_size)

#             # Convert PIL images to TensorFlow tensors
#             original_tensor = tf.convert_to_tensor(original_image, dtype=tf.float32) / 255.0
#             style_tensor = tf.convert_to_tensor(style_image, dtype=tf.float32) / 255.0
#             original_tensor = tf.expand_dims(original_tensor, axis=0)  # Add batch dimension
#             style_tensor = tf.expand_dims(style_tensor, axis=0)

#             # Perform style transfer with the model
#             stylized_output_tensor = model(original_tensor, style_tensor)

#             # Convert the stylized tensor to a PIL image
#             stylized_image = tensor_to_image(stylized_output_tensor)

#             # Save and respond with the image
#             response_image = save_image_to_response(stylized_image)
#             return HttpResponse(response_image, content_type="image/png")

#         else:
#             return HttpResponse("Please upload both an original image and a style image.", status=400)

#     return render(request, 'upload_page.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after login
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        
        if password != confirm_password:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        user = User.objects.create_user(username, email, password)
        user.save()
        login(request, user)
        return redirect('home')  # Redirect to the homepage after registration
    
    return render(request, 'register.html')

def upload_images(request):
    if request.method == 'POST':
        
        original_image_file = request.FILES.get('original_image')
        style_image_file = request.FILES.get('style_image')

        if original_image_file and style_image_file:
            
            original_path = default_storage.save(original_image_file.name, original_image_file)
            style_path = default_storage.save(style_image_file.name, style_image_file)

            original_image_url = default_storage.url(original_path)
            style_image_url = default_storage.url(style_path)

           
            original_image = Image.open(original_image_file).convert('RGB')
            style_image = Image.open(style_image_file).convert('RGB')

            
            target_size = (256, 256) 
            original_image = original_image.resize(target_size)
            style_image = style_image.resize(target_size)

            
            original_tensor = tf.convert_to_tensor(original_image, dtype=tf.float32) / 255.0
            style_tensor = tf.convert_to_tensor(style_image, dtype=tf.float32) / 255.0

           
            original_tensor = tf.expand_dims(original_tensor, axis=0)
            style_tensor = tf.expand_dims(style_tensor, axis=0)

            
            try:
                stylized_output_tensor = model(original_tensor, style_tensor)
                stylized_image = tensor_to_image(stylized_output_tensor)

                # Save the result
                result_path = f"styled_{original_image_file.name}"
                stylized_image.save(default_storage.path(result_path))
                result_image_url = default_storage.url(result_path)
            except Exception as e:
                return HttpResponse(f"Error during style transfer: {e}", status=500)

           
            uploaded_images = default_storage.listdir('')[1] 
            uploaded_images_urls = [default_storage.url(img) for img in uploaded_images]

            # Render the result
            return render(request, 'style_transfer.html', {
                'original_image_url': original_image_url,
                'style_image_url': style_image_url,
                'result_image_url': result_image_url,
                'uploaded_images': uploaded_images_urls
            })
        else:
            return HttpResponse("Please upload both an original image and a style image.", status=400)

    return render(request, 'style_transfer.html')

def three_d_images_page(request):
    return render(request, '3d_images_page.html')

def generate_3d_from_canvas(request):
    if request.method == 'POST':
        # Decode the base64 image
        data = request.json().get('image')
        header, encoded = data.split(',', 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_data))
        
        # Process the image with your 3D synthesis model
        # Placeholder: generated_image = some_model_process(image)

        # Simulate response
        response_data = {
            'generated_image_url': '/static/img/generated_sample.png',
        }
        return JsonResponse(response_data)

def generate_3d(request):
    if request.method == 'POST' and 'input_image' in request.FILES:
        input_image = request.FILES['input_image']
        # Process the uploaded file with your 3D synthesis model
        # Placeholder: generated_image = some_model_process(input_image)

        # Simulate response (Save the output somewhere accessible)
        return JsonResponse({'message': '3D Image generated successfully!'})
def art_gallery(request):
    artworks = Artwork.objects.all()
    return render(request, 'art_gallery.html', {'artworks': artworks})

def upload_art(request):
    if request.method == 'POST' and request.FILES['artwork']:
        artwork = request.FILES['artwork']
        title = artwork.name.split('.')[0]  # Use file name as title
        fs = FileSystemStorage()
        file_path = fs.save(artwork.name, artwork)
        artwork_url = fs.url(file_path)

        Artwork.objects.create(title=title, url=artwork_url)
        return redirect('art_gallery')

    return redirect('art_gallery')
def home(request):
    return render(request, 'home.html')