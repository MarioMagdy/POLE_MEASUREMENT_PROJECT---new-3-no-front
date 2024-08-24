import numpy as np
import torch
from utils.datasets import letterbox
from models.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords

def detect_pole(img0, model, device):
    img = letterbox(img0, 640)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device).float()
    img /= 255.0  # Normalize
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    pred = model(img)[0]
    pred = non_max_suppression(pred, 0.3, 0.5)  # Use standard thresholds for now

    # Extract bounding boxes
    det = pred[0]
    if len(det):
        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()

    boxes =None
    # Assuming the top and bottom bounding boxes represent the pole
    if len(det) >= 2:
        boxes = sorted(det[:, :4].tolist(), key=lambda x: x[1])  # sort by y-coordinates
        
    return boxes



def load_model(weights_path= "weights/pole_98.pt"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = attempt_load(weights_path, map_location=device)  # Load a small YOLOv5 model (assuming it's in the directory)
    model.to(device).eval()
    return model,device

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = attempt_load("weights/pole_98.pt", map_location=device)  # Load a small YOLOv5 model (assuming it's in the directory)
    model.to(device).eval()
    
    image_path = 'pole_image2.jpg'
    boxes = detect_pole(image_path, model, device)
    print(boxes)
    
   

