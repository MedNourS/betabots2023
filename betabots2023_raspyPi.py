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
import robotpy_apriltag as rpat
import logging
import ntcore
import math

# Function to detect AprilTags and estimate pose
def pose_estimation(frame, estimator, size):

    # Create an AprilTag detector
    detector = rpat.AprilTagDetector()
    detector.addFamily("tag36h11")

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect AprilTags in the grayscale frame
    detections = detector.detect(gray_frame)

    # Process each detection
    for detection in detections:
        
        # Get tag information
        tag_id = detection.getId()
        x, y = detection.getCenter().x, detection.getCenter().y

        # Use the pose estimator to estimate the tag's pose
        pose = rpat.AprilTagPoseEstimator(estimator).estimate(detection)
        translation = pose.translation()
        rotation = pose.rotation()
        pitch, yaw, roll = rotation.x_degrees, rotation.y_degrees, rotation.z_degrees
        
        # Get all AprilTag corners
        pt1 = detection.getCorner(0)
        pt2 = detection.getCorner(1)
        pt3 = detection.getCorner(2)
        pt4 = detection.getCorner(3)
        
        #* AprilTag Corners Demonstration
        #*     pt1 -> O -- -- -- -- O <- pt2
        #*            |             |
        #*            |             |
        #*            |             |
        #*            |             |
        #*     pt4 -> O -- -- -- -- O <- pt3

        # Pixel Length of Side 1 (pt1 to pt4)
        yLength1 = abs(pt1.y - pt4.y)
        xLength1 = abs(pt1.x - pt4.x)
        pixelSideLength1 = ((xLength1)**2+(yLength1)**2)**0.5

        # Pixel Length of Side 2 (pt2 to pt3)
        yLength2 = abs(pt2.y - pt3.y)
        xLength2 = abs(pt2.x - pt3.x)
        pixelSideLength2 = ((xLength2)**2 + (yLength2)**2)**0.5

        # Calculate Distance from Camera to AprilTag
        tagDistance = (size * 650) / ((pixelSideLength1 * pixelSideLength2) ** 0.5)

        # Returns the AprilTag information
        return [tag_id, int(x), int(y), round(pitch, 2), round(yaw, 2), round(roll, 2), round(tagDistance, 2)]


# Main function
def main():

    # Print (NetworkTables) status updates in CLI
    logging.basicConfig(level=logging.DEBUG)

    # Start a NetworkTables instance, initialize NetworkTables4 client and set Server
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.startClient4("raspyPi")
    inst.setServer("192.168.0.113") #! Change IP with server's IP

    # Fetch Table, Topic and Publisher
    table = inst.getTable("9076")
    publish = table.getFloatArrayTopic("april").publish()

    # Open the camera (0 is usually the default camera)
    cap = cv2.VideoCapture(0)
    
    # Create an AprilTag pose estimator configuration
    tag_size = 0.1778  # Replace with the actual size of your AprilTag in meters
    fx, fy, cx, cy = 1000.0, 1000.0, 640.0, 480.0  #! Replace with your camera's intrinsic parameters
    estimator_config = rpat.AprilTagPoseEstimator.Config(tag_size, fx, fy, cx, cy)

    while True:
        
        # Capture a frame from the camera and return it
        ret, frame = cap.read()
        # If no frames are returned, stop the program
        if not ret:
            break

        # Variable for [tag_id, x, y, pitch, yaw, roll, tagDistance]
        poseList = pose_estimation(frame, estimator_config, tag_size)

        # Publish AprilTag information; if no AprilTag is detected, publish [-1, -1, -1, -1, -1, -1, -1]
        try:
            publish.set(poseList)
        except:
            publish.set([-1, -1, -1, -1, -1, -1, -1])

if __name__ == "__main__":
    main()
