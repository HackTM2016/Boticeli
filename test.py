import cv2
import numpy as np

#used to use multiple cascades
car_cascade = [cv2.CascadeClassifier('test.xml')]
colors = [(0,255,0)]

#open video
cap = cv2.VideoCapture('inter3.avi')

#dimensions of video
wid = 1280
hei = 698

scale = 2 #we divide by this

#defines our intersection
#points = np.array([(50,125),(900,60),(1280,150),(1280,260),(244,450)])
points = np.array([(50,175),(500,120),(900,150),(900,290),(180,480)])
entries = [(50,175),(410,130),(650,130),(820,145),(900,290),(900,190), (50,175),(180,480)]
exits = [(410,130),(500,120),(500,120),(650,130),(820,145),(900,150),(900,150),(900,190),(900,290),(180,480)]

id = 0

v_points = {}
v_points_entry = {}
v_points_exit = {}

def distToLine(line_s, line_e, point):
    normalLength = np.hypot(line_e[0] - line_s[0], line_e[1] - line_s[1])
    distance = np.abs((point[0] - line_s[0]) * (line_e[1] - line_s[1]) - (point[1] - line_s[1]) * (line_e[0] - line_s[0])) / normalLength
    return distance

def distToLineArr(line_arr, point):
    dist = 99999
    for i in range (0, len(line_arr)/2):
        d = distToLine(line_arr[2*i],line_arr[2*i+1], point)
        if d<dist:
            dist = d
    return dist

#check if x is within the image
def checkX(origX):
    if origX < 0:
        return 0
    elif origX > wid:
        return wid
    else:
        return origX

#check if y is within the image
def checkY(origY):
    if origY < 0:
        return 0
    elif origY > hei:
        return hei
    else:
        return origY

def distance((a1,b1),(a2,b2)):
    return np.sqrt(np.power(a1-a2,2)+np.power(b1-b2,2))

#main loop
while cap.isOpened():

    #image aquisition and cascade detection
    ret, orig_1 = cap.read()

    if ret:
        break

    frame = cv2.resize(orig_1, (0,0), fx=0.75, fy=0.75)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cars = car_cascade[0].detectMultiScale(gray, 1.1, 1)

    current_points = list()

    #detect cascades and display them
    for i in range(0, len(points)):
        cv2.line(frame,(points[i][0],points[i][1]),(points[(i+1)%len(points)][0],points[(i+1)%len(points)][1]),(255,0,0),3)

    for (x, y, w, h) in cars:
        center = (x+w/2,y+h/2)

        area = w * h;

        if area<5000:
            continue

        if cv2.pointPolygonTest(points, center, False) >= 0:
            current_points.append(center)
            cv2.rectangle(frame, (x, y), (x + w, y + h), colors[0], 2)
            cv2.circle(frame, center, 10, (255,0,0))

    for i in range(0,4):
        cv2.line(frame,entries[i*2],entries[i*2+1], (0,0,0),3)

    for i in range(0, 5):
        cv2.line(frame, exits[i * 2], exits[i * 2 + 1], (0, 0, 255), 3)

    #go through list of identified cascades
    for (x,y) in current_points:
        found = False
        min = 99999
        min_id = 0
        min_point = (x,y)

        for i,(m,n) in v_points.iteritems():
            dist = distance((x,y),(m,n))
            if dist < 300/scale and dist < min:
                min = dist
                found = True
                min_id = i
                min_point = (x,y)


        if(cv2.pointPolygonTest(points, (x,y), True)) >= 15/scale:
            if found:
                v_points[min_id] = min_point
            else:
                d = distToLineArr(exits, min_point)
                if d > 50:
                    v_points[id] = min_point
                    v_points_entry[id] = min_point
                    id = id +1

    to_be_deleted = list()

    for i,(x,y) in v_points.iteritems():
        cv2.circle(frame, (x,y), 25, (255,255,255))
        cv2.putText(frame, str(i), (x,y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (255, 255, 255), 2)

        if i in v_points_entry:
            d = distToLineArr(exits,(x,y))
            if d < 25:
                v_points_exit[i] = (x, y)
                to_be_deleted.append(i)

    for i in to_be_deleted:
        v_points.pop(i,None)

    for i,(x,y) in v_points_entry.iteritems():
        cv2.circle(frame, (x, y), 25, (0, 255, 0))
        cv2.putText(frame, str(i), (x, y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 255, 0), 2)

    for i, (x, y) in v_points_exit.iteritems():
        cv2.circle(frame, (x, y), 25, (0, 0, 255))
        cv2.putText(frame, str(i), (x, y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()