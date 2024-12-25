from ultralytics import YOLO
import cv2
import streamlit as st
from PIL import Image
import numpy as np

# Load YOLO model
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

# Process and display the detection results
def display_results(image, results):
    boxes = results.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
    scores = results.boxes.conf.cpu().numpy()  # Confidence scores
    labels = results.boxes.cls.cpu().numpy()  # Class indices
    names = results.names  # Class names
    
    for i in range(len(boxes)):
        if scores[i] > 0.5:  # Confidence threshold
            x1, y1, x2, y2 = boxes[i].astype(int)
            label = names[int(labels[i])]
            score = scores[i]
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label}: {score:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

# Main Streamlit app
def main():
    st.title("")
    st.sidebar.title("Settings")
    
    model_path = "best.pt"  # Path to your YOLO model
    model = load_model(model_path)

    # Create the checkbox once
    run_detection = st.sidebar.checkbox("Start/Stop Object Detection", key="detection_control")

    # Open video capture if checkbox is active
    if run_detection:
        cap = cv2.VideoCapture(0)
        st_frame = st.empty()  # Placeholder for video frames

        while True:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture image.")
                break

            # Run YOLO detection
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for display
            results = model.predict(frame, imgsz=640)  # Perform detection
            
            # Draw results
            frame = display_results(frame, results[0])
            st_frame.image(frame, channels="RGB", use_column_width=True)

            # Break the loop if checkbox is unchecked
            if not st.session_state.detection_control:
                break
        
        cap.release()

if __name__ == "__main__":
    main()