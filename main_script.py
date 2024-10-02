import ModelFunctions
import cv2
from UserModelLogic import DetectionDecisionLogic_v3
import ImageScales
from Interface import interface
import numpy as np
from PIL import Image
import os
from datetime import datetime
import csv
# datetime object containing current date and time

class MainScript:
    def __init__(self) -> None:
        # add /home/MarioMagdy/mysite
        self.model, self.device = ModelFunctions.load_model('weights/pole_98.pt')
        self.interface1 = interface()
        self.detection_logic = DetectionDecisionLogic_v3(show= False,threshold=25)

    def initiate(self,img0,user_base_cords):
        self.img0 = img0
        self.box_preds = ModelFunctions.detect_pole(img0,self.model,self.device)

        if self.box_preds is not  None:
            img_with_preds = self.interface1.draw_boxes_image(img0,self.box_preds)
        else:
            img_with_preds = img0.copy()


        self.final_base_coords = self.detection_logic.get_the_correct_detection(img0,user_base_cords,self.box_preds)
        # detection_logic.is_error_accepted
        img_with_final_base = self.interface1.draw_boxes_image(img0,[self.interface1.get_box_from_point(self.final_base_coords)])
        self.img_with_final_base = img_with_final_base

        return img_with_preds, img_with_final_base,self.final_base_coords



    def get_scale_of_image_fov(self,image,base_coordinates):
        try:
            img_scale_fov = ImageScales.ImageScaleUsingFOV(image,base_coordinates)
            return img_scale_fov
        except AssertionError:
            print("Error: Image does not have a valid FOV")



    def get_scale_of_image_ref(self,image:Image,final_base_coords,end_of_measurement_stick_cords,reference_stick_length = None):
        # img_with_preds_resized, _ = self.interface1.resize_image(img_with_preds)
        # cv2.putText(img_with_preds_resized, 'The AI Prediction', (10, 30),
        #                         cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        # interface1.show_img(img_with_preds_resized)
        img0 = np.array(image)
        max_di = max(img0.shape)

        ###############
        height_of_measurement_stick = self.detection_logic.distance_formula(end_of_measurement_stick_cords,final_base_coords)
        end_of_measurement_stick_box = self.interface1.get_box_from_point(end_of_measurement_stick_cords,  box_size=max_di/4000*20)
        final_image = self.interface1.draw_boxes_image(img0,[end_of_measurement_stick_box])
        ###############

        reference = {'name':"measurement stick"
             ,'height in inches': 216.535}

        if reference_stick_length:
            reference['height in inches'] = reference_stick_length

        image_scaler_ref = ImageScales.ImageScaleUsingReference(image,height_of_measurement_stick,base_coordinates=final_base_coords,reference=reference)

        return final_image,image_scaler_ref


    def get_point_height(self,final_image,point,image_scaler):

        height =image_scaler.get_height_in_inches(point)

        # img_with_user_click = self.interface1.draw_boxes_image(final_image,[self.interface1.get_box_from_point(point,  box_size=10)])
        return height
        # img_with_user_click_resized, _ = self.interface1.resize_image(img_with_user_click)

        # cv2.putText(img_with_user_click_resized, f'Height is: {round(height/12,2)}', (10, 100),
        #                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # self.interface1.show_img(img_with_user_click_resized)

    def save_user_input_for_model_training(self,training_data_path,final_base_coords,image):
        # Save the image for training
        now = datetime.now()
        d_now  = now.strftime("%Y-%m-%d %H-%M-%S")
        img_name = f"{d_now}.png"
        img_path = os.path.join(training_data_path, img_name)
        image.save(img_path)

        # Save the corresponding base coordinates in a CSV file
        csv_path = os.path.join(training_data_path, "base_coordinates.csv")
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([img_name, final_base_coords[0], final_base_coords[1]])
