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

# Function to detect apriltag and estimate pose
def pose_estimation(frame, estimator, size):

    # Create an AprilTag detector
    detector = rpat.AprilTagDetector()
    detector.addFamily("tag36h11")

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect AprilTags in the grayscale frame
    detections = detector.detect(gray_frame)
    
    # Total AprilTags detected
    detectedTags = 0

    # Process each detection
    for detection in detections:
        
        # For every detection, add a detected AprilTag
        detectedTags += 1

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

        #*    AprilTag Corners Demonstration
        #*
        #*     pt1 -> O ---------- O <- pt2
        #*            |            |
        #*            |            |
        #*            |            |
        #*            |            |
        #*     pt4 -> O ---------- O <- pt3

        # Length 1
        yLength1 = abs(pt1.y - pt4.y)
        xLength1 = abs(pt1.x - pt4.x)
        pixelSideLength1 = ((xLength1)**2+(yLength1)**2)**0.5

        # Length 2
        yLength2 = abs(pt2.y - pt3.y)
        xLength2 = abs(pt2.x - pt3.x)
        pixelSideLength2 = ((xLength2)**2 + (yLength2)**2)**0.5

        # Calculate average pixel side length (of length 1 and 2)
        #// avgSidePixelLength = (pixelSideLength1 + pixelSideLength2)/2

        #tagDistance = (size / avgSidePixelLength)*1000 - 0.55
        tagDistance = (size * 650) / ((pixelSideLength1 * pixelSideLength2) ** 0.5)
             
    # Returns the AprilTag information
    try:
        return [tag_id, int(x), int(y), round(pitch, 2), round(yaw, 2), round(roll, 2), round(tagDistance, 2), detectedTags]
    except:
        return None

# Main function
def main():

    # Print status updates in CLI
    logging.basicConfig(level=logging.DEBUG)

    # Initialize NT4 client
    inst = ntcore.NetworkTableInstance.getDefault()
    inst.startClient4("raspyPi")
    inst.setServer("192.168.0.111") #! Change IP with server's IP

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
        # Capture a frame from the camera
        ret, frame = cap.read()

        if not ret:
            break
        frame = cv2.resize(frame, (1280, 720))

        # Fetch AprilTag information from pose_estimation()
        poseList = pose_estimation(frame, estimator_config, tag_size)
        
        #? For testing purposes
        #// print(poseList)

        # Detect and estimate poses for AprilTags in the captured frame
        try:
            publish.set(poseList)
        except:
            publish.set([-1, -1, -1, -1, -1, -1, -1, -1])

if __name__ == "__main__":
    main()