# OpenCV BallTracking Tutorial

The following script is meant to detect, localize, and track a colored ball using the OpenCV computer vision Python library.
As output, the script show the screen with a detected ball and a contrail following the movement of the ball.
Additionally, the script generates a .svg file with a plot of Theta vs. Time (the ball's angular velocity) and a .csv file with the ball's X and Y coordinates plus time and theta values.

To read the writeup, either open the OpenCV_BallTracking_Tutorial .pdf file or to compile as a LateX document, use the folder.

### Requirements and Libraries
The libraries required for this tutorial include NumPy, OpenCV, Matplotlib, Pandas, and imutils.
Exact requirements are specified in the requirements.txt file.

### Running
**Video Options:** <br>
To run the script using a built in webcam, use: ```python OpenCV_BallTracker.py```. <br>
To run the script using a pre-recorded .mp4 video, use: ```python OpenCV_BallTracker.py --video file.mp4```.

**Buffer Options:** <br>
To change the size of the buffer (length of contrail), use: ```python OpenCV_BallTracker.py --buffer buffer_int```. <br>
The default buffer size is set to 64.
A larger buffer size creates a longer contrail and vice-versa.

To quit running while in webcam mode, press 'q'.
If a pre-recorded video is supplied, running will end after video end, but 'q' still works.

### Outputs <br>
Succesfully running the script generates a .svg file plotting Theta vs. Time and a .cvs file with the ball's X and Y coordinates plus time and theta values.
To change where these files are written, go to bottom of OpenCV_BallTracker.py file and change the file path in the Data_df.to_csv() method and in the plt.savefig() method.
