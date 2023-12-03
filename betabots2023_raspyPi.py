#                            _____ _ 
#                           |  __ (_)
#  _ __ __ _ ___ _ __  _   _| |__) _ 
# | '__/ _` / __| '_ \| | | |  ___| |
# | | | (_| \__ | |_) | |_| | |   | |
# |_|  \__,_|___| .__/ \__, |_|   |_|
#               | |     __/ |        
#               |_|    |___/         

#*#*# For a better viewing experience, install the Better Comments extension for VSCode #*#*#

# Modules
import cv2
import numpy as np
import robotpy_apriltag as rpat
import logging
import ntcore

# Function to detect apriltag and estimate pose
def pose_estimation_and_communication(frame, estimator):
    
    #* Network Tables: 
    # Print status updates in CLI
    logging.basicConfig(level=logging.DEBUG)

    # Initialize NT4 client
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.startClient4("raspyPi")
    inst.setServer("192.168.0.21") #! Change IP with server's IP

    # Fetch Table, Topic and Publisher
    table = inst.getTable("values")
    publish = table.getFloatArrayTopic("idexidy").publish()

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create an AprilTag detector
    detector = rpat.AprilTagDetector()
    detector.addFamily("tag36h11")

    # Detect AprilTags in the grayscale frame
    detections = detector.detect(gray_frame)

    # Process each detection
    for detection in detections:
        # Get tag information
        tag_id = detection.getId()
        x, y = detection.getCenter().x, detection.getCenter().y

        # Print the information
        print(f"[tag= {tag_id}, x= {x}, y= {y}]")

        # Use the pose estimator to estimate the tag's pose
        pose = estimator.estimate(detection)
        translation = pose.translation()
        rotation = pose.rotation()
        roll, pitch, yaw = rotation.x, rotation.y, rotation.z

        # Publish values to /values/idexidy
        publish.set([id, x, y, yaw])

# Main function
def main():

    # Open the camera (0 is usually the default camera)
    cap = cv2.VideoCapture(2)

    # Create an AprilTag pose estimator configuration
    tag_size = 0.1778  # Replace with the actual size of your AprilTag in meters
    fx, fy, cx, cy = 1000.0, 1000.0, 640.0, 480.0  # Replace with your camera's intrinsic parameters
    estimator_config = rpat.AprilTagPoseEstimator.Config(tag_size, fx, fy, cx, cy)

    # Create an AprilTag pose estimator with the specified configuration
    estimator = rpat.AprilTagPoseEstimator(estimator_config)

    while True:
        # Capture a frame from the camera
        ret, frame = cap.read()

        # Detect and estimate poses for AprilTags in the captured frame
        pose_estimation_and_communication(frame, estimator)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()