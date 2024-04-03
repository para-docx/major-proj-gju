import cv2

camera = cv2.VideoCapture("http://192.168.1.6:4747/video")

# Check if camera opened successfully 
if (camera.isOpened()== False): 
	print("Error opening video file") 

# Read until video is completed 
while(camera.isOpened()): 
	
# Capture frame-by-frame 
	ret, frame = camera.read() 
	if ret == True: 
	# Display the resulting frame 
		cv2.imshow('Frame', frame) 
		
	# Press Q on keyboard to exit 
		if cv2.waitKey(25) & 0xFF == ord('q'): 
			break
# Break the loop 
	else: 
		break

# When everything done, release 
# the video capture object 
camera.release() 

# Closes all the frames 
cv2.destroyAllWindows()