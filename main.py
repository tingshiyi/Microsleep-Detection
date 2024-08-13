import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import pygame
import threading

# Initialize Pygame mixer in the main thread
pygame.init()
pygame.mixer.init()

# Function to play sound in a separate thread to avoid blocking
def play_sound(sound_file):
    def play():
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    threading.Thread(target=play, daemon=True).start()

# Path to your sound file
sound_file_path = 'correct-156911.mp3'  # Replace with the actual path

# Open webcam
cap = cv2.VideoCapture(0)

# Only detect one face
detector = FaceMeshDetector(maxFaces=1)

# Define the landmark IDs for eyes and mouth
idList1 = [243, 22, 24, 130, 160, 158, 385, 252, 254, 463, 387, 359, 61, 72, 302, 291, 315, 85]

# Initialize live plots
plotY = LivePlot(640, 360, [20, 52])
plotMouthRatio = LivePlot(640, 360, [20, 100])
plotYawning = LivePlot(640, 360, [0, 5])

# Initialize variables
ratioList = []
mouthRatioList = []
counter = 0
color = (255, 0, 255)
update_rate = 30
yolo_detect = 0

# Get start time in seconds
tick_frequency = cv2.getTickFrequency()
startTime = cv2.getTickCount() / tick_frequency
start_time_one_seconds = startTime
start_time_two_seconds = startTime
start_time_one_minute = startTime
start_time_half_minute = startTime

Blink_one_minute = 0
Blink_one_second = 0
Blink_Two_second = 0

# One second duration
OneSecondDuration = 1

# Two second duration
TwoSecondDuration = 2

# One minute duration in seconds
oneMinuteDuration = 40

# Variable to track the time "Yawning" was displayed
yawningDisplayTime = 0
MicrosleepDisplayTime = 0

# Yawning time in one minute
Yawning_Number = 0
Yawning_Number_Over = 0

while True:
    # Read the video and detect face mesh
    success, img = cap.read()
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        face = faces[0]
        for id in idList1:
            cv2.circle(img, face[id], 5, (255, 0, 255), cv2.FILLED)

        # Calculate eye ratio left
        Left_P1, Left_P2, Left_P3, Left_P4, Left_P5, Left_P6 = face[243], face[22], face[24], face[130], face[160], face[158]
        LengthHorLeftEyes, _ = detector.findDistance(Left_P1, Left_P4)
        LeftLengthVerLeft, _ = detector.findDistance(Left_P2, Left_P6)
        LeftLengthVerRight, _ = detector.findDistance(Left_P3, Left_P5)
        cv2.line(img,Left_P1,Left_P4,(0,200,0),3)
        cv2.line(img,Left_P2,Left_P6, (0, 200, 0), 3)
        cv2.line(img,Left_P3,Left_P5, (0, 200, 0), 3)

        # Calculate eye ratio right
        Right_P1, Right_P2, Right_P3, Right_P4, Right_P5, Right_P6 = face[385], face[252], face[254], face[463], face[387], face[359]
        LengthHorRightEyes, _ = detector.findDistance(Right_P1, Right_P4)
        RightLengthVerLeft, _ = detector.findDistance(Right_P2, Right_P6)
        RightLengthVerRight, _ = detector.findDistance(Right_P3, Right_P5)
        cv2.line(img, Right_P6, Right_P4, (0, 200, 0), 3)
        cv2.line(img, Right_P1, Right_P2, (0, 200, 0), 3)
        cv2.line(img, Right_P3, Right_P5, (0, 200, 0), 3)

        # Calculate the mouth ratio
        M_P1, M_P2, M_P3, M_p4, M_P5, M_P6 = face[61], face[72], face[302], face[291], face[315], face[85]
        HorMouth, _ = detector.findDistance(M_P1, M_p4)
        LengthVerLeftMouth, _ = detector.findDistance(M_P2, M_P6)
        LengthVerRightMouth, _ = detector.findDistance(M_P3, M_P5)

        # Calculate Mouth Ratio
        mouthRatio = int(((LengthVerLeftMouth + LengthVerRightMouth) / (2 * HorMouth)) * 100)
        mouthRatioList.append(mouthRatio)
        cv2.line(img, M_P1, M_p4, (0, 200, 0), 3)
        cv2.line(img, M_P2, M_P6, (0, 200, 0), 3)
        cv2.line(img, M_P3, M_P5, (0, 200, 0), 3)

        # Calculate the eyes ratio
        ratio = int((LeftLengthVerLeft + LeftLengthVerRight) / (2 * LengthHorLeftEyes) * 100)
        ratioList.append(ratio)
        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)

        # Normal Timeline
        currentTime = cv2.getTickCount() / tick_frequency
        elapsedTime = currentTime - startTime

        if ratioAvg < 32:
            if counter == 0:
                color = (0, 200, 0)
                counter = 1

            if counter != 0:
                counter += 1
                if counter > 10:
                    counter = 0
                    color = (255, 0, 255)

            elapsedTime_one_seconds = currentTime - start_time_one_seconds
            elapsedTime_two_seconds = currentTime - start_time_two_seconds

            if elapsedTime_one_seconds >= OneSecondDuration:
                print("Close eyes more than 3 seconds")
                Blink_one_second = 1
                start_time_one_seconds = currentTime

            if elapsedTime_two_seconds >= TwoSecondDuration:
                print("Close eyes more than 3 seconds")
                Blink_Two_second = 1
                start_time_two_seconds = currentTime
        else:
            start_time_one_seconds = currentTime
            start_time_two_seconds = currentTime

        # Calculate elapsed time since start (1 minute)
        elapsedTime_one_minute = currentTime - start_time_one_minute

        # Check if one minute has elapsed
        if elapsedTime_one_minute >= oneMinuteDuration:
            start_time_one_minute = currentTime
            Yawning_Number_Over = 0
            if Yawning_Number >= 4:
                Yawning_Number_Over = 1

        # Output of the blinking number
        # cvzone.putTextRect(img, f'Blink Count: {blinkCounter}', (50, 100), colorR=color)

        # Condition of yawning and active
        if (Blink_one_second == 1) and (mouthRatio > 70):
            yawningDisplayTime = currentTime  # Update yawning display time
            play_sound(sound_file_path)  # Play the sound alert
            Blink_one_second = 0
            Yawning_Number = Yawning_Number + 1

        elif currentTime - yawningDisplayTime < 1:  # Display "Yawning" for at least 2 seconds
            cvzone.putTextRect(img, 'Yawning', (50, 50), colorR=(0, 0, 255))  # Red color for yawning
            cvzone.putTextRect(img, 'Buzzer On', (50, 100), colorR=(0, 0, 255))

        else:
            cvzone.putTextRect(img, 'Active', (50, 50), colorR=(0, 255, 0))
            Blink_one_second = 0

        if (Blink_Two_second == 1) or (Yawning_Number_Over == 1):
            play_sound(sound_file_path)  # Play the sound alert
            MicrosleepDisplayTime = currentTime  # Update yawning display time
            Yawning_Number_Over = 0
            Blink_Two_second = 0

        elif currentTime - MicrosleepDisplayTime < 10:  # Display "Yawning" for at least 10 seconds
            cvzone.putTextRect(img, 'Microsleep', (50, 100), colorR=(0, 0, 255))  # Red color for yawning
            cvzone.putTextRect(img, 'Buzzer On', (50, 150), colorR=(0, 0, 255))


        # Blinking graph
        imgPlot = plotY.update(ratioAvg)
        imgMouthPlot = plotMouthRatio.update(mouthRatio)
        imgYawning = plotYawning.update(Yawning_Number)

        # Resize the video
        img = cv2.resize(img, (640, 360))

        # Combine the graph and the video capture
        imgStack = cvzone.stackImages([img, imgPlot, imgMouthPlot, imgYawning], 2, 1)

    else:
        cvzone.putTextRect(img, 'No face detected', (50, 50), colorR=(0, 0, 255))  # Red color for yawning
        img = cv2.resize(img, (640, 360))
        imgStack = cvzone.stackImages([img, img], 2, 1)

    # Showing the window
    cv2.imshow("image", imgStack)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()