# API Documentation for Image Processing Backend

## Overview

This API provides endpoints to process images by allowing users to initiate image analysis, scale images based on reference points, and estimate heights based on image data. The API is built using Flask and leverages sessions to maintain state across requests. It supports CORS, session management, and rate limiting.

## Base URL

```
http://localhost:5500
```

## Endpoints

### 1. `/initiate` (POST)

**Description:**  
Initiates the image analysis process. It accepts an image and base coordinates, performs initial processing, and stores the results in the session.

**Request Parameters:**
- **image** (file): The image file to be processed.
- **base_coordinates** (string): A comma-separated string representing the base coordinates (e.g., `"x,y"`).

**Response:**
- **200 OK:**
  - `got_scale` (boolean): Indicates if the image scale was successfully calculated.
  - `model_predicted_correctly` (boolean): Whether the model prediction was accepted.
  - `final_base_coords` (tuple): The final base coordinates used for further calculations.
- **400 Bad Request:**
  - `error` (string): Error message indicating the issue with the request.

**Example Request:**

```bash
curl -X POST -F "image=@path/to/image.png" -F "base_coordinates=100,200" http://localhost:5500/initiate
```

### 2. `/scale_using_reference` (POST)

**Description:**  
Scales the image using a reference point provided by the user. This endpoint must be called after the `/initiate` endpoint.

**Request Parameters:**
- **reference_point** (string): A comma-separated string representing the reference point coordinates (e.g., `"x,y"`).

**Response:**
- **200 OK:**
  - `got_scale` (boolean): Indicates if the image scale was successfully calculated using the reference point.
- **400 Bad Request:**
  - `error` (string): Error message indicating missing image data or reference point.

**Example Request:**

```bash
curl -X POST -d "reference_point=150,250" http://localhost:5500/scale_using_reference
```

### 3. `/estimate_height` (POST)

**Description:**  
Estimates the height of a point in the image based on the scaling information set in previous steps.

**Request Parameters:**
- **height_point** (string): A comma-separated string representing the coordinates of the point whose height needs to be estimated (e.g., `"x,y"`).

**Response:**
- **200 OK:**
  - `height` (float): The estimated height of the point in the image.
- **400 Bad Request:**
  - `error` (string): Error message indicating missing data or failure to initiate the process.
- **500 Internal Server Error:**
  - `error` (string): Error message indicating an issue during height estimation.

**Example Request:**

```bash
curl -X POST -d "height_point=300,400" http://localhost:5500/estimate_height
```

## Session Management

- **Session Type:** Filesystem-based
- **Session Lifetime:** 5 minutes of inactivity
- The session data is automatically cleaned up after each request to ensure no stale data remains on the server.

## Rate Limiting

- **200 requests per day per IP address**
- **50 requests per hour per IP address**

## Error Handling

All endpoints return standard HTTP status codes along with a JSON object containing an `error` key when an error occurs.

## Running the Server

To run the Flask server, use the following command:

```bash
python app.py
```

- **Port:** 5500
- **Debug Mode:** Enabled

## Dependencies

- Flask
- Flask-Session
- Flask-CORS
- Flask-Limiter
- OpenCV (`cv2`)
- NumPy
- PIL (Python Imaging Library)

Ensure all dependencies are installed before running the server.

## Notes

- This API is intended for image processing tasks where image scaling and height estimation are required based on user input.
- Make sure to handle large image uploads carefully due to the maximum allowed content length of 16 MB.

---

This documentation should help in understanding the API's capabilities and how to interact with it.