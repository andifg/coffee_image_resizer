# Import the Images module from pillow
from PIL import Image
import sys
import os
import io

# Get the current working directory
dir = sys.path[0]
execution_path = os.getcwd()


buf = io.BytesIO()

# print("The current working directory is:", dir)
# print("The current working directory is:", execution_path)

# Open the image by specifying the image path.
image_path = f"{execution_path}/test.jpg"
print("The image path is:", image_path)
image_file: Image = Image.open(image_path)


# the default
image_file.save("image_name.jpg", quality=20)


file_stats_new = os.stat("image_name.jpg")
file_stats_old = os.stat(image_path)

# Save to buffer

image_file.save(buf, format="JPEG", quality=20)


print(f"File Size in MegaBytes is { round(file_stats_old.st_size / (1024 * 1024), 2)}")

w, h = image_file.size
print("width: ", w)
print("height:", h)
print("#######################")

print(f"File Size in MegaBytes is { round(file_stats_new.st_size / (1024 * 1024), 2)}")
w_new, h_new = Image.open("image_name.jpg").size
print("width: ", w_new)
print("height:", h_new)


print("#######################")
print(f"File Size in MegaBytes is { round(len(buf.getvalue()) / (1024 * 1024), 2)}")
w_new, h_new = Image.open(io.BytesIO(buf.getvalue())).size
print("width: ", w_new)
print("height:", h_new)

print("#######################")

# Set the image size and color
width, height = 3024, 4032
red_color = (255, 0, 0)  # RGB values for red

# Create a new image with a red background
image = Image.new("RGB", (width, height), red_color)

print(
    "Image in Buffer size: ", round(sys.getsizeof(image.tobytes()) / (1024 * 1024), 2)
)

# Save the image to the current working directory

new_byte = io.BytesIO()

image.save("red_image.jpg")

image.save(new_byte, format="JPEG")

print(
    f"File Size in MegaBytes is { round(len(new_byte.getvalue()) / (1024 * 1024), 2)}"
)


def resize_image():
    pass


# # Changing the image resolution using quality parameter
# # Example-1
# image_file.save("image_name2.jpg", quality=25)

# # Example-2
# image_file.save("image_name3.jpg", quality=1)
