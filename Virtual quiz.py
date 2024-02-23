import cv2
import csv
import time
import cvzone
from cvzone.HandTrackingModule import HandDetector
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)
class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])
        self.userAns = None

    def update(self, cursor, bboxs):
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1<cursor[1]<y2:
                self.userAns = x + 1
                cv2.rectangle(img,(x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
pathCSV = "virtual.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    data = list(reader)[1:]
mcqList = []
for q in data:
    mcqList.append(MCQ(q))
qNo = 0
qTotal = len(data)
prevRect = [50, 50, 150, 100]
nextRect = [1000, 50, 1150, 100]

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

# Add buttons
    cv2.rectangle(img, (prevRect[0]+ 150, prevRect[1]+ 450) +(prevRect[0] + prevRect[2], prevRect[1] + prevRect[3]),
                  (255, 0, 255), 3)
    cv2.putText(img, "Previous", (prevRect[0] + 150, prevRect[1] + 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.rectangle(img, (nextRect[0], nextRect[1]), (nextRect[0] + nextRect[2], nextRect[1] + nextRect[3]),
                  (255, 0, 255), 3)
    cv2.putText(img, "Next", (nextRect[0] + 10, nextRect[1] + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if qNo<qTotal:

        mc = mcqList[qNo]
        img, bbox = cvzone.putTextRect(img, mc.question, [100, 100], 2, 2, offset=50, border=5)
        img, bbox1 = cvzone.putTextRect(img, mc.choice1, [100, 250], 2, 2, offset=50, border=5)
        img, bbox2 = cvzone.putTextRect(img, mc.choice2, [400, 250], 2, 2, offset=50, border=5)
        img, bbox3 = cvzone.putTextRect(img, mc.choice3, [100, 400], 2, 2, offset=50, border=5)
        img, bbox4 = cvzone.putTextRect(img, mc.choice4, [400, 400], 2, 2, offset=50, border=5)

        if hands:
            lmlist=hands[0]['lmList']
            cursor=lmlist[8]
            length,info=detector.findDistance(lmlist[8][0:2], lmlist[12][0:2])

            if prevRect[0]<cursor[0]<prevRect[0]+prevRect[2] and prevRect[1]<cursor[1]<prevRect[1]+prevRect[3]:
                qNo -= 1

            if nextRect[0]<cursor[0]<nextRect[0]+nextRect[2] and nextRect[1]<cursor[1]<nextRect[1]+nextRect[3]:
                qNo += 1

            if qNo < 0:
                qNo = 0

            if qNo >= len(mcqList):
                qNo = len(mcqList)-1

            if length<=30 and length>=20:
                mc.update(cursor,[bbox1,bbox2,bbox3,bbox4])
                print(mc.userAns)
                if mc.userAns is not None:
                    time.sleep(0.9)
                    qNo +=1

    else:
        score = 0
        for mc in mcqList:
            if mc.answer==mc.userAns:
                score+=1
        score=round((score/qTotal)*100,2)

        img, _ = cvzone.putTextRect(img,"Quiz Completed", [250, 300], 2, 2, offset=50,border=5)
        img, _ = cvzone.putTextRect(img, f'Your Score:{score}%', [700, 300], 2, 2, offset=50,border=5)

    barValue=150+(950//qTotal)*qNo
    cv2.rectangle(img, (150, 600), (barValue, 650), (255, 0, 0), cv2.FILLED)
    cv2.rectangle(img,(150,600),(1100,650),(255,0,255),5)
    img, _= cvzone.putTextRect(img, f'{round((qNo/qTotal)*100)}%', [1130, 635], 2, 2, offset=15)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 81 or key == 113:
        break