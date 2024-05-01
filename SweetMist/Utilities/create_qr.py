import qrcode
from PIL import Image, ImageDraw

def generate_transparent_qr_code_with_link(link, color='#fff', file_path='qrcode.png', bg_color='#000'):
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(link)
    qr.make(fit=True)

    # Create QR code image with alpha channel for transparency
    qr_img = qr.make_image(fill_color=color, back_color=bg_color)

    # Convert to RGBA mode for transparency
    qr_img = qr_img.convert("RGBA")

    # Create a transparent layer
    transparent_layer = Image.new("RGBA", qr_img.size, (255, 255, 255, 0))

    # Composite the QR code and the transparent layer
    final_image = Image.alpha_composite(transparent_layer, qr_img)

    # Save the image
    final_image.save(file_path)

    print(f"Transparent QR code with link '{link}' and color '{color}' and background color '{bg_color}' generated and saved to '{file_path}'.")

if __name__ == "__main__":
    website_link = 'https://www.sweetmist.in/'  # Replace with your desired link
    generate_transparent_qr_code_with_link(website_link, color='#fff', bg_color='#6a2249')
