import numpy as np
from Interface import interface


interface1 = interface()

        
import numpy as np

## taking the distance from the bottom line of the prediction box to increase the accuracy
class DetectionDecisionLogic_v3():
    def __init__(self, threshold=33,show=True):
        self.threshold = threshold
        self.show=show
        self.use_box = False
        self.pred_points = 0
        self.img_scale = 0
        self.error = 0
        self.error_scaled = 0
        self.bot_ind = 0
        self.bot_pred_point = 0
        self.bot_error_accepted = 0
        self.error_bot_point_scaled = 0
        self.prediction_error = 0
        self.is_error_accepted = 0
        self.did_model_predict = 0


    def get_center_of_box(self,box):
        return ((box[0]+box[2])//2,(box[1]+box[3])//2)

    def distance_formula(self, p1, p2):
        return np.sqrt(np.sum((np.array(p1) - np.array(p2)) ** 2))
    

    def load_bot_pred_from_box(self,box):
            # in the base box we are getting the bottom line middle point 
            bot_box = self.get_lower_box(box)
            # print('lower box is ',bot_box)
            self.bot_pred_point = ((bot_box[0]+bot_box[2])//2 , bot_box[3])
            return self.bot_pred_point


    def set_scale(self,img_scale):
        self.img_scale = img_scale

    
    def compare_points(self,model_pred_p,user_input_p):
        "Don't call it, This function compares point in the detection results from the model and user input then returns the result"

        # print(model_pred_p,user_input_p)
        print(model_pred_p,user_input_p)

        self.error = self.distance_formula(model_pred_p,user_input_p)
        self.error_scaled = self.error*self.img_scale

        if self.error_scaled >= self.threshold:
            if self.show:
                print("The error is too high, Model Probably Wrong...")
            return False
        
        else:
            if self.show:
                print("The error is acceptable, Model is probably correct...")
            return True
        


    def get_lower_box(self,boxes):
        """
        This function takes a list of bounding boxes and returns the box that is located lowest on the image.
        
        Parameters:
            boxes (list of list of float): A list of bounding boxes, where each box is represented as [x_min, y_min, x_max, y_max].

        Returns:
            list of float: The bounding box with the largest y_max value.
        """
        if not boxes:
            return None

        # Initialize with the first box
        lower_box = boxes[0]
        max_y = boxes[0][3]  # y_max of the first box

        for box in boxes[1:]:
            if box[3] > max_y:  # Compare y_max of the current box with the max_y
                lower_box = box
                max_y = box[3]

        return lower_box


    def process_model_preds(self,pred_points):
        "Don't call it, This function processes the detection results from the model"
        number_of_points = len(pred_points)

        if number_of_points==0 :
            return None
            
        bot_pred_point = self.get_bot_pred(pred_points)
        return bot_pred_point

            

    def get_bot_pred(self,pred_points):
        "Don't call it, Finds the lowest point in the prediction to be the bottom of the pole"
        bot = 0
        for ind,pred in enumerate(pred_points):
            if pred[1] == max(pred_points, key=lambda x:x[1])[1]:
                self.bot_ind = ind

                break

        self.bot_pred_point = pred_points[self.bot_ind]

        return pred_points[self.bot_ind]


        
    
    # def compare_detections(self,user_base_cords,pred_points):
    #     "This function compares the detection results from the model and user input then returns the result"
    #     ## fix the cases of
    #     # 1- if model doesn't have predictions  ✔
    #     # 2- model predicts more than 2 ✔
    #     # 3- model predicts top as bot and bot as top ✔
    #     # ...


    def get_the_correct_detection(self,img,user_base_cords,pred_boxes):
        # print(self.compare_detections(user_base_cords,pred_points))
        self.prediction_error = 0
        if not pred_boxes:
            self.bot_error_accepted = 0
            self.did_model_predict = 0
            self.prediction_error = 1
            print("No Model prediction")
            return user_base_cords ## No model predictions
        
        img_resized,scale = interface1.resize_image(img)

        self.set_scale(scale)

        self.did_model_predict = 1

        bot_pred_point = self.load_bot_pred_from_box(pred_boxes)

        self.bot_error_accepted = self.compare_points(bot_pred_point,user_base_cords)
        

        if self.bot_error_accepted:
            return self.bot_pred_point
        
        else:
            return user_base_cords


        
