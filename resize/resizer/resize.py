# Import the Images module from pillow
from PIL import Image
import sys
import os
import io


class ImageResizer:

    def reduze_quality(self,image_data: bytes, quality: int = 20):

        image = Image.open(io.BytesIO(image_data))

        new_byte = io.BytesIO()

        image.save(new_byte, format="JPEG", quality=quality)

        size = round(len(new_byte.getvalue()) / (1024 * 1024), 2)

        print(
        f"File Size in MegaBytes is {size} for qaulity {quality}"
        )

        new_byte.seek(0)

        if size > 0.3 and quality > 5:
            print("Image size is greater than 0.3 MB")
            return self.reduze_quality(image_data, quality=quality - 3)

        else:
            return new_byte