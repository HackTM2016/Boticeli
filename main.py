import cv2
import numpy as np

#used to use multiple cascades
car_cascade = [cv2.CascadeClassifier('test.xml')]
colors = [(0,255,0)]

#open video
cap = cv2.VideoCapture('inter9.avi')

#dimensions of video
wid = 1280
hei = 698

scale = 2 #we divide by this

#defines our intersection
#points = np.array([(0,0),(1280,0),(1280,720),(0,720)])
points = np.array([(50,155),(500,110),(900,150),(900,290),(180,480)])
entries = [(50,155),(410,115),(630,120),(820,145),(900,290),(900,190), (75,230),(180,480)]
exits = [(410,115),(500,110),(500,110),(640,120),(820,145),(900,150),(900,150),(900,190),(900,290),(180,480),(75,230),(50,155)]

id = 0

v_points = {}
v_points_entry = {}
v_points_exit = {}
v_points_check = {}

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

f_count = 0

time = 1

ret, stat = cap.read() #read an initial frame

stat = cv2.resize(stat, (0,0), fx=0.75, fy=0.75)

#main loop
while cap.isOpened():
    #image aquisition and cascade detection
    ret, orig_1 = cap.read()

    f_count += 1

    if not ret:
        break

    e1 = cv2.getTickCount()

    frame = cv2.resize(orig_1, (0,0), fx=0.75, fy=0.75)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cars = car_cascade[0].detectMultiScale(gray, 1.1, 1)

    current_points = list()

    cv2.putText(frame, "Frame:" +str(f_count), (20,40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255),1)
    cv2.putText(frame, "Cars:" + str(id), (20, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 1)
    cv2.putText(frame, "FPS:" + str(int(1/time)), (20, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 1)
    # if f_count > 180:
    #     if cv2.waitKey(10000) & 0xFF == ord('q'):
    #         break

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

    for i in range(0, 6):
        cv2.line(frame, exits[i * 2], exits[i * 2 + 1], (0, 0, 255), 3)

    #go through list of identified cascades
    for (x,y) in current_points:
        found = False
        min = 99999
        min_id = 0
        min_point = (x,y)

        #cv2.circle(frame, (x, y), 10, (122, 122, 122),5)
        #cv2.putText(frame, str(x)+";"+str(y), (x, y+15), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (255, 255,255))

        for i, (m, n) in v_points.iteritems():
            dist = distance((x,y),(m,n))

            #print "Distance from x,y:"+str(x)+";"+str(y)+" circle to id "+str(i) +": "+str(dist)+" at " + str(m)+";"+str(n)

            #cv2.line(frame, (x,y), (m,n), (122, 122, 0), 3)
            if dist < 300/scale and dist < min:
                min = dist
                found = True
                min_id = i
                min_point = (x,y)

        if cv2.pointPolygonTest(points, (x,y), True) >= 15:
            if found:
                v_points[min_id] = min_point
            else:
                d = distToLineArr(exits, min_point)
                if d > 50:
                    v_points[id] = min_point
                    v_points_entry[id] = min_point
                    temp = (min_point, f_count)
                    v_points_check[id] = temp
                    id = id +1

    to_be_deleted = list()

    for i,(x,y) in v_points.iteritems():
        cv2.circle(frame, (x,y), 25, (255,255,255))
        cv2.putText(frame, str(i), (x,y), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (255, 255, 255), 2)

        #print "Id " + str(i) + "is at "+str(x)+";"+str(y)
        d2 = 3000
        if i in v_points_entry:
            d = distToLineArr(exits,(x,y))
            d2 = distance(v_points_entry[i],(x,y))

            #print "Distance to exit:" + str(d)+ "; distance to entry: "+str(d2)

            if d < 30 and d2 > 70:
                v_points_exit[i] = (x, y)
                to_be_deleted.append(i)

        #v_points_check will remember the position of a point so that it can be removed if it stays stationary for too long
        var = v_points_check[i]
        if var[0] != (x,y):
            v_points_check[i] = ((x,y),f_count)
        else:
            cv2.circle(frame, (x, y), 25, (0, 0, 255),2)
            dte = distToLineArr(exits,(x,y))
            if dte<60 and d2 > 70:
                v_points_exit[i] = (x, y)
                to_be_deleted.append(i)
            # else:
            #     print "Id "+str(i)+"is this far away from exit: "+str(dte)


        if f_count - v_points_check[i][1] > 10:
            to_be_deleted.append(i)

    for i in to_be_deleted:
        v_points.pop(i,None)
        v_points_check.pop(i,None)

    for i,(x,y) in v_points_entry.iteritems():
        cv2.circle(frame, (x, y), 5, (0, 255, 0))
        cv2.putText(frame, str(i), (x+5, y+5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.75, (0, 255, 0))

    for i, (x, y) in v_points_exit.iteritems():
        cv2.circle(frame, (x, y), 5, (0, 0, 255))
        cv2.putText(frame, str(i), (x+5, y+5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.75, (0, 0, 255))

    #frame = cv2.resize(frame, (0, 0), fx=1.35, fy=1.35)

    e2 = cv2.getTickCount()

    time = (e2 - e1) / cv2.getTickFrequency()

    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.waitKey()

#process data

print "Begging processing"

print "Remove duplicates"

obsolete = []

for i,(x,y) in v_points_entry.iteritems():
    if not(i in v_points_exit):
        obsolete.append(i)

for i in obsolete:
    v_points_exit.pop(i,None)

obsolete = []

for i, (x, y) in v_points_exit.iteritems():
    if not (i in v_points_entry):
        obsolete.append(i)

for i in obsolete:
    v_points_entry.pop(i, None)

incoming = [np.array([(140,170),(440,440),(870,325),(400,145)]),np.array([(633,147),(556,202),(700,256),(822,171)]),
            np.array([(825,175),(700,255),(872,326),(955,208)]),np.array([(440,440),(204,227),(82,265),(185,508)])]

going = [np.array([(153,168),(509,138),(788,170),(700,256)]),np.array([(788,167),(960,208),(950,326),(705,254)]),
         np.array([(904,315),(700,255),(142,412),(184,500)]),np.array([(94,283),(233,240),(155,166),(53,180)])]

for j in range(0,4):
    for i in range(0, len(incoming[j])):
        cv2.line(stat, (incoming[j][i][0], incoming[j][i][1]), (incoming[j][(i + 1) % len(incoming[j])][0], incoming[j][(i + 1) % len(incoming[j])][1]),(0, 255, 0), 3)
    for i in range(0, len(going[j])):
        cv2.line(stat, (going[j][i][0], going[j][i][1]),(going[j][(i + 1) % len(going[j])][0], going[j][(i + 1) % len(going[j])][1]), (0, 0, 255), 3)

for i, (x, y) in v_points_entry.iteritems():
    cv2.circle(stat, (x, y), 5, (0, 255, 0))
    cv2.putText(stat, str(i), (x + 5, y + 5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.75, (0, 255, 0))

for i, (x, y) in v_points_exit.iteritems():
    cv2.circle(stat, (x, y), 5, (0, 0, 255))
    cv2.putText(stat, str(i), (x + 5, y + 5), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.75, (0, 0, 255))

cv2.imshow('frame',stat)

fo = open("data.out", "w")

mat = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

for i,(x,y) in v_points_entry.iteritems():
    a1 = -1
    b1 = -1
    for j in range (0,4):
        #print "Point "+str(x)+","+str(y)+"; zone check "+str(i)+": "+str(cv2.pointPolygonTest(incoming[j], (x,y), True))
        if cv2.pointPolygonTest(incoming[j], (x,y), False) >= 0:
            a1 = j
            break

    print "i:"+str(i)

    if i in v_points_exit:
        (m,n) = v_points_exit[i]
        for j in range(0, 4):
            if cv2.pointPolygonTest(going[j], (x, y), False) >= 0:
                b1 = j
                break

    if a1 != -1 and b1 != -1:
        mat[a1][b1] += 1

    #print "a1, b1: "+str(a1)+";"+str(b1)

for j,(x1,y1) in v_points_exit.iteritems():
    print "j:"+str(j)


for i in range(0,4):
    for j in range(0,4):
        fo.write(str(mat[i][j])+" ")
    fo.write("\n")

fo.close()

cv2.waitKey()

# When everything done, release the capture

cv2.destroyAllWindows()