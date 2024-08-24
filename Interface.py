import cv2
import numpy as np

class interface:
    def __init__(self, conf_thres=0.25, iou_thres=0.45, imgsz=640, show_predictions=True, box_size=15):

        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.imgsz = imgsz
        self.show_predictions = show_predictions
        self.box_size = box_size
        self.colors = self._generate_colors()
        self.point = ()
        self.user_clicks = []
        self.pred_boxes = []
        self.pred_points= []

    def _generate_colors(self, num_colors=10):
        colors = []
        for _ in range(num_colors):
            color = np.random.randint(0, 255, size=(3,))
            color = (int(color[0]), int(color[1]), int(color[2]))
            colors.append(color)
        return colors

    def set_mouse_callback(self, event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.point = (x, y)
            self.user_clicks.append(self.point)
            if len(self.user_clicks) == 2:
                cv2.destroyAllWindows()


    def draw_boxes_image(self, img, boxes):
        dim = max(img.shape)
        img2= img.copy()
        for box in boxes:
            x1, y1, x2, y2 = [int(i) for  i in box]
            img2 = cv2.rectangle(img2, (x1, y1), (x2, y2), (120, 100, 170), int((dim/2400)* 15))
            
        return img2
    
    def show_img(self,img):
        while True:
            cv2.imshow('Pole Detection', img)
            key = cv2.waitKey(1)
            if key == 27:  # Enter key
                cv2.destroyAllWindows()
                break


    def get_box_from_point(self,point,box_size=30):
        # print(point,box_size)
        return point[0]-box_size//2, point[1]-box_size//2,point[0]+box_size//2, point[1]+box_size//2


    def show_img_resized(self,img):
        img2,_ = self.resize_image(img)
        self.show_img(img2)


    def show_img_with_points_as_boxes(self,img,points,box_size=20):

        for point in points:
            img_with_user_click = self.draw_boxes_image(img,[self.get_box_from_point(point,  box_size=box_size)])

        img_with_user_click_resized, _ = self.resize_image(img_with_user_click)
        self.show_img(img_with_user_click_resized)
        return img_with_user_click


    def resize_image(self, img, target_height=900):
        h, w, _ = img.shape
        scale = target_height / h
        target_width = int(w * scale)
        resized_img = cv2.resize(img, (target_width, target_height))
        return resized_img, scale

    def get_user_input(self, img:np.array, message = 'Click at the base then press Enter',shape='box',text_s = 0.8):
        self.user_clicks =[]
        resized_img, scale = self.resize_image(img)
        # print("Scale: ",scale)
        cv2.namedWindow('Pole Detection', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Pole Detection', self.set_mouse_callback)

        while True:
            display_img = resized_img.copy()
            if len(self.user_clicks) != 0:
                break

            cv2.putText(display_img, message, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, text_s, (0, 255, 0), 2)

            for idx, click in enumerate(self.user_clicks):
                color = self.colors[idx % len(self.colors)]
                if shape == 'box':
                    cv2.rectangle(display_img, 
                                (click[0]-self.box_size//2, click[1]-self.box_size//2), 
                                (click[0]+self.box_size//2, click[1]+self.box_size//2), 
                                color, 2)
                    
                else:
                    cv2.circle(display_img, click, 5, color, 2)


            cv2.imshow('Pole Detection', display_img)
            key = cv2.waitKey(1)
            if key == 13 and len(self.user_clicks) >= 1:  # Enter key
                break

        cv2.destroyAllWindows()
        return self.user_clicks[0][0]/scale,self.user_clicks[0][1]/scale



    def get_user_input2(self, img:np.array, messages = ['Click at the base then press Enter'],shape='box',text_s = 0.8):
        self.user_clicks =[]
        resized_img, scale = self.resize_image(img)
        # print("Scale: ",scale)
        cv2.namedWindow('Pole Detection', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Pole Detection', self.set_mouse_callback)

        while True:
            display_img = resized_img.copy()
            if len(self.user_clicks) != 0:
                break

            for ind,message in enumerate (messages):
                cv2.putText(display_img, message, (10, 30+30*ind),
                            cv2.FONT_HERSHEY_SIMPLEX, text_s, (0, 255, 0), 2)

            for idx, click in enumerate(self.user_clicks):
                color = self.colors[idx % len(self.colors)]
                if shape == 'box':
                    cv2.rectangle(display_img, 
                                (click[0]-self.box_size//2, click[1]-self.box_size//2), 
                                (click[0]+self.box_size//2, click[1]+self.box_size//2), 
                                color, 2)
                    
                else:
                    cv2.circle(display_img, click, 5, color, 2)


            cv2.imshow('Pole Detection', display_img)
            key = cv2.waitKey(1)
            if key == 13 and len(self.user_clicks) >= 1:  # Enter key
                break

        cv2.destroyAllWindows()
        return self.user_clicks[0][0]/scale,self.user_clicks[0][1]/scale

        
    
    

    def height_formula_pixels(self, p1, p2):
        return p1[1]-p2[1]