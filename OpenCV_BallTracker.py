# Import necessary libraries
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2 as cv
import imutils
import time
import pandas as pd
import matplotlib.pyplot as plt


'''
Initialization:
- Argument parsing
- Create deque
- Set video/pre-recorded
- Create DataFrame to hold ball positions
'''

# construct the argument parse and parse the arguments on script call
ap = argparse.ArgumentParser()
# For tracking ball from .mp4 video
ap.add_argument("-v", "--video",
	help="optional path for video file")
# Buffer size corresponds to length of deque
# Larger buffer = longer ball contrail
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args, unknown = ap.parse_known_args()
args_dict = vars(args)

# define the lower and upper boundaries of the ball
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

# Initialize deque for list of tracked coords using buffer size
coords = deque(maxlen=args_dict["buffer"])

# Check if no video was supplied and set to camera
# else, grab a reference to the video file
if not args_dict.get("video", False):
	camera = cv.VideoCapture(0)
else:
	camera = cv.VideoCapture(args_dict["video"])
 
# allow the camera or video file to warm up
time.sleep(2.0)

# Create DataFrame to hold coordinates and time
data_columns = ['x', 'y', 'time']
data_df = pd.DataFrame(data = None, columns=data_columns, dtype=float)

# Read time at video start
start = time.time()

'''
Pre-Processing:
- Grab camera frame 
- Save current time
- Resize frame, blur frame, convert to HSV
- Construct "green" mask and perform erosion/dilation
'''

while True:
    
	# grab current camera frame
	(grabbed, frame) = camera.read()
	
	# Check current time
	current_time = time.time() - start

	# if video supplied and no frame grabbed, video ended so break
	if args_dict.get("video") and not grabbed:
		break

	# resize frame, blur it, and convert from BGR to HSV color space
	frame = imutils.resize(frame, width=1000)
	blurred = cv.GaussianBlur(frame, (11, 11), 0)
	hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform dilation and erosion to remove remaining minor blobs in mask
	mask = cv.inRange(hsv, greenLower, greenUpper)
	mask = cv.erode(mask, None, iterations=2)
	mask = cv.dilate(mask, None, iterations=2)
 
 
	'''
	Ball Localization:
	- Find contours in frame
	- Keep largest contour and validated against minimum and maximum radius
	- Update contour position
	- Draw circle over ball and center of ball
 	'''

	# find contours in the mask and initialize the current (x, y) coordinate center of the ball
	cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL,
		cv.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
     
		# find largest contour in mask, then compete minimum enclosing circle and contour centroid
		c = max(cnts, key=cv.contourArea)
		((x, y), radius) = cv.minEnclosingCircle(c)
		M = cv.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# Only draw if radius within acceptable range
		if (radius < 300) & (radius > 10 ) : 
      
			# draw the circle and centroid on the screen
			cv.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
			cv.circle(frame, center, 5, (0, 0, 255), -1)
			
			# Save positions in DataFrame
			data_df.loc[data_df.size/3] = [x , y, current_time]

	# update the position queue
	coords.appendleft(center)

	'''
 	Contour Drawing:
	- Loop over deque buffer size
	- Check current and past point for values
	- Draw line between values
  	'''

	# loop over deque for tracked position
	for i in range(1, len(coords)):
     
		# Ignore drawing if curr/past position is None
		if coords[i - 1] is None or coords[i] is None:
			continue

		# Compute line between positions and draw
		thickness = int(np.sqrt(args_dict["buffer"] / float(i + 1)) * 2.5)
		cv.line(frame, coords[i - 1], coords[i], (0, 0, 255), thickness)

	# show the frame to screen
	cv.imshow("Frame", frame)
	key = cv.waitKey(1) & 0xFF

	# Stop tracking/end loop when 'q' pressed
	if key == ord("q"):
		break


'''
Output Generation:
- Camera lens and shift correction
- Calculate theta value
- Create plot of Theta vs. Time
- Export DataFrame as .csv and plot as .svg

'''

h = 0.2 # focal length of camera
X0 = -3 # shift correction for x-axis
Y0 = 20 # shift ocrrection for y-axis
theta0 = 0.3 # theta correction

# Apply correction values to each x, y, and time value
data_df['x'] = data_df['x']- X0
data_df['y'] = data_df['y'] - Y0

# Calculate theta using arctan of y and camera correction
data_df['theta'] = 2 * np.arctan(data_df['y']*0.0000762/h) # factor corresponds to real-world pixel length
data_df['theta'] = data_df['theta'] - theta0

# Generate Theta vs. Time Plot
plt.plot(data_df['theta'], data_df['time'])
plt.title('Ball Angular Velocity (Theta vs. Time)')
plt.xlabel('Theta')
plt.ylabel('Time')

# Export plot and DataFrame
data_df.to_csv('Data_Set.csv', sep=",")
plt.savefig('Time_vs_Theta_Graph.svg', transparent= True)

# Release camera and destroy webcam video
camera.release()
cv.destroyAllWindows()