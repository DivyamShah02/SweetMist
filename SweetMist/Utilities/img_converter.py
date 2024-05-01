from PIL import Image

# Open the image
image = Image.open(r"C:\Users\divya\OneDrive\Desktop\Sweet Mist\SweetMist\Media\Product_Img\Untitled_design_6.webp")

# Resize the image
resized_image = image.resize((70, 70))

# Save the resized image
resized_image.save("output_image.webp")
