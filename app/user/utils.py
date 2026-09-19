import base64
from bs4 import BeautifulSoup
import io 
import os
import secrets
from PIL import Image
from flask import url_for
from flask_mail import Message
from flask import current_app
from app import mail
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)

def save_picture(form_picture, output_size=(125, 125)):
    """Uploads an image to Cloudinary, resizes it in the cloud,

    and returns the permanent secure HTTPS URL.
    """
    # Cloudinary handles resizing directly during upload
    upload_result = cloudinary.uploader.upload(
        form_picture,
        folder="profile_pics",  # Optional: keeps uploads organized in Cloudinary
        transformation=[
            {
                "width": output_size[0],
                "height": output_size[1],
                "crop": "thumb",
                "gravity": "face",
            } 
        ],
    )

    # Return the secure HTTPS URL to store in Neon DB
    return upload_result["secure_url"]


def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for("user.reset_password", token=token, _external=True)

    msg = Message(
        "Password Reset Request",
        sender='s11smehar432@gmail.com',
        recipients=[user.email],  # no need to specify sender, uses MAIL_DEFAULT_SENDER
    )

    msg.body = f"""To reset your password, visit the following link:

{reset_url}

If you did not request this, simply ignore this email.
"""

    mail.send(msg)

def process_embedded_images(html_content, max_size=(1200, 1200)):
    """
    Parses HTML content, finds base64 encoded <img> tags, converts them to compressed image files,
    saves them in static/pics, and returns the updated HTML content with file paths.
    """
    if not html_content:
        return html_content

    soup = BeautifulSoup(html_content, 'html.parser')
    images = soup.find_all('img')

    upload_folder = os.path.join(current_app.root_path, "static", "pics")
    os.makedirs(upload_folder, exist_ok=True)

    for img in images:
        src = img.get('src', '')
        # Check if the image source is a base64 string
        if src.startswith('data:image/'):
            try:
                # Extract header and base64 data
                header, encoded = src.split(',', 1)
                image_data = base64.b64decode(encoded)

                # Open with Pillow
                image = Image.open(io.BytesIO(image_data))
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Resize image to save memory and space
                image.thumbnail(max_size)

                # Generate a unique filename
                random_hex = secrets.token_hex(8)
                filename = f"{random_hex}.jpg"
                filepath = os.path.join(upload_folder, filename)

                # Save compressed JPEG image
                image.save(filepath, 'JPEG', quality=85)

                # Replace the giant Base64 src with the static file URL
                img['src'] = f"/static/pics/{filename}"
            except Exception as e:
                # If conversion fails for any reason, keep existing src or log error
                print(f"Error processing image: {e}")
                continue

    return str(soup)