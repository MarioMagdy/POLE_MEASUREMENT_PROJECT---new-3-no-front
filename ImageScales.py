
from PIL import Image
from PIL.ExifTags import TAGS
import math
import numpy as np


class ImageScaleUsingFOV:
    def __init__(self,image:Image,base_coordinates) -> None:
        self.image = image
        self.base_coordinates = base_coordinates
        self.image_width_pixels,self.image_height_pixels = self.image.size
        # get_exif_data()
        self.get_fov_of_image()


    
    def get_exif_data(self):
        exif_data = self.image._getexif()
        exif = {}
        if exif_data:
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                exif[decoded] = value
        self.exif = exif
        return exif
    
    def get_fov_of_image(self):
        
        self.exif_data = self.get_exif_data()
        assert ('FocalLengthIn35mmFilm'  in self.exif_data), f"FocalLengthIn35mmFilm is not available in the metadata of this image"

        self.FL = self.exif_data['FocalLengthIn35mmFilm']
        
        self.fov_vertical_deg = 2 * math.atan(35 / (2 * self.FL)) * (180 / math.pi)
        # return self.fov_vertical_deg
    
    def get_height_in_inches(self,point,object_distance=10):
        # Calculate the real-world object height
        height_in_pixels = self.distance_formula(self.base_coordinates,point)

        fov_vertical_rad = math.radians(self.fov_vertical_deg)
        H_real = 2 * object_distance * math.tan(fov_vertical_rad / 2) * (height_in_pixels / self.image_height_pixels)
        # print(f"Real-world object height: {H_real:.2f} meters")
        return H_real
    
    def distance_formula(self, p1, p2):
        return np.sqrt(np.sum((np.array(p1) - np.array(p2)) ** 2))
    



## For now we are going to find the POV of the image using reference in this case the mesurement stick 
## which in most cases has a length of 5.5m ~= 18ft ~= 216.535inch
# user_clicks = self.get_user_input(img,"Click the top of the measurement stick",shape=point_shape)
# point_height = self.get_height_in_pixels(self.final_bot_point, user_clicks)
# self.pixels_per_inch = point_height/216.535


# reference = {'name':"measurement stick"
#              ,'height in inches': 216.535}


class ImageScaleUsingReference:
    
    def __init__(self,image:Image,reference_height_pixels,base_coordinates,
                 reference = {'name':"measurement stick" ,'height in inches': 216.535}
             ) -> None:
    
        
        self.image = image
        # print(self.image.size)
        self.image_width_pixels,self.image_height_pixels = self.image.size

        self.reference = reference
        self.reference_height_pixels = reference_height_pixels
        
        self.calc_scale(reference_height_pixels)
        self.base_coordinates = base_coordinates


    def calc_scale(self,reference_height_pixels):
        self.pixels_per_inch= reference_height_pixels /self.reference['height in inches']
        self.pixels_per_ft= reference_height_pixels /(self.reference['height in inches']/12)

    
    def get_height_in_inches(self,point):
        height_in_pixels = self.distance_formula(self.base_coordinates,point)
        height_in_inches = height_in_pixels/self.pixels_per_inch
        return height_in_inches
    

    def distance_formula(self, p1, p2):
        return np.sqrt(np.sum((np.array(p1) - np.array(p2)) ** 2))
    

if __name__ == '__main__':
    ImageScaleUsingFOV('pole_image2.jpg')
    