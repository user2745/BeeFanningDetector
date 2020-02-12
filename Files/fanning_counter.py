import cv2
import numpy as np
import time

d_frames={}
rects={}
#convert input frame to threshold using background subtraction
def to_thresh(img,bk):
    

    subImage=(bk.astype('int32')-img.astype('int32')).clip(0).astype('uint8')
    grey=cv2.cvtColor(subImage,cv2.COLOR_BGR2GRAY)
    retval,thresh=cv2.threshold(grey,35,255,cv2.THRESH_BINARY_INV)
    thresh=255-thresh
    kernel=np.ones((5,5),np.uint8)
    thresh=cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel)
    return thresh

#compare current bee contours with fanning bee reference contours
#and find match.
def detect_fanning(c1):
    for i in range(3):
        fname="C:/Users/obrienam/Documents/GitHub/BeeFanningDetector/Assets/fan_ref/thresh_"+str(i+1)+".jpg"
        f=cv2.imread(fname)
       
        f=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        im3, cnts2, hierarchy2 = cv2.findContours(f, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for c2 in cnts2:
            a1=cv2.contourArea(c1)
            a2=cv2.contourArea(c2)
            #compare the two contour areas
            
            m=cv2.matchShapes(c1,c2,cv2.CONTOURS_MATCH_I1,0.0)
            if m<=0.3:
                a=a1/a2
                if(a<=1.1):
                    return m
                else:
                    continue
    return 1000

#Compare the area, central point, and shape
#of two contours to determine if the bee was stationary.
def cmpContours(frame,c1,c2):
    match=cv2.matchShapes(c1,c2,cv2.CONTOURS_MATCH_I1,0.0)

    mom1=cv2.moments(c1)
    cx1 = int(mom1["m10"] / mom1["m00"])
    cy1 = int(mom1["m01"] / mom1["m00"])
    mom2=cv2.moments(c2)
    cx2 = int(mom2["m10"] / mom2["m00"])
    cy2 = int(mom2["m01"] / mom2["m00"])
    cx=cx1/cx2
    cy=cy1/cy2

    a1=cv2.contourArea(c1)
    a2=cv2.contourArea(c2)
    a=a1/a2
    detected=False
    
    if (cx <= 1.0 and cx >= 0.95 and cy <= 1.0 and cy >= 0.95 
        and a <= 1.0 and a >= 0.95 and a1 < 10000 and match <= 0.1):
        for c in range(cx1-20,cx1+20):
            if(d_frames.get(c) is not None):
                x,y,w,h=rects.get(c)
                frame=frame[y:y+h,x:x+w]
                d_frames[c].append(frame)
                detected=True
        if(d_frames.get(cx1) is None and detected==False):
            #print("recognized" + str(cx1))
            x,y,w,h=cv2.boundingRect(c1)
            frame=frame[y:y+h,x:x+w]
            d_frames[cx1]=[frame]
            rects[cx1]=[x,y,w,h]
        '''
        elif(d_frames.get(cx1) is not None):
            print("append" + str(cx1))
            x,y,w,h=cv2.boundingRect(c2)
            frame=frame[y:y+h,x:x+w]
            d_frames[cx1].append(frame)
        else:
            print("first " + str(cx1))
            x,y,w,h=cv2.boundingRect(c1)
            frame=frame[y:y+h,x:x+w]
            d_frames[cx1]=[frame]
        '''
        return True
    
    return False

#remove moving/not fanning bees from threshold frame
#and count total number of fanning bees
def rem_movement(im,thresh,cnt1,cnt2):
    #loop through first conotur list
    numFan=0
    cntmoving=[]
    for c1 in cnt1:
        found=False
        
        #loop through second contour list
        for c2 in cnt2:
            #check if bee was stationary and was in the 
            #size range of a staionary bee
            if c1.size>460 and cmpContours(im,c1,c2):
                #if match, stop searching
                #Experimental fanning code to be completed later
                '''
                m2=detect_fanning(c1)
                
                if m2 <= 0.3:
                    #print("fan")
                    if(c1.size > 530 and c1.size < 635):
                        #print(3)
                        numFan = numFan+3
                    elif(c1.size>460):
                        #print(1)
                        numFan = numFan+1
                    #cntmoving.append(c1)
                else:
                    cntmoving.append(c1)
                
                rect=cv2.boundingRect(c1)
                x,y,w,h=rect
                cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),2)
                '''
                found=True
                #break
        if(found==False):
            #if not found, append it to moving contours
            cntmoving.append(c1)
    
    #fill contours that moved with white
    cv2.drawContours(thresh, cntmoving, -1, (0,0,0), -1)
    return thresh,numFan

def make_vids(d_frames):
    i = 0
   
    for key in d_frames:
        frames=d_frames[key]
        if(len(frames)>1):
            
            height, width, layers = frames[0].shape
            size = (width,height)
            out = cv2.VideoWriter('../Assets/stationary_bees/out_'+str(key)+'.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (size))
            for f in frames:
                out.write(f)
            out.release()
            i=i+1

#main driver function
def main():
    #windows video file path
    vs=cv2.VideoCapture("C:/Users/obrienam/Documents/GitHub/BeeFanningDetector/Assets/test_vid1.mp4")
    #mac video file path
    #vs=cv2.VideoCapture("/Users/aidanobrien/Documents/GitHub/BeeFanningDetector/Assets/test_vid1.mp4")

    img1=None
   

    #loop through video frames 

    while True:
        hasFrames,img2=vs.read()
        if (hasFrames==False):
            break
        
        if img1 is not None:
            #mac file path
            #bk=cv2.imread('/Users/aidanobrien/Documents/GitHub/BeeFanningDetector/Assets/testbkgrd1.jpg')
           
            bk=cv2.imread('C:/Users/obrienam/Documents/GitHub/BeeFanningDetector/Assets/testbkgrd1.jpg')
            
            
            bk=bk[75:75+315,0:0+637]
            img2=img2[75:75+315,0:0+637]
            

            #take first threshold
            thresh1=to_thresh(img1,bk)
            #find first set of frame contours
            im2, contours1, hierarchy1 = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            #cv2.drawContours(img1, contours1, -1, (0,255,0), 3)
            
            #find second threshold
            thresh2=to_thresh(img2,bk)
            #find second set of frame contours
            im3, contours2, hierarchy2 = cv2.findContours(thresh2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

            #remove contours of moving/non-fanning bees and count fanning bees
            thresh1,curFan=rem_movement(img1,thresh1,contours1,contours2)
            #show treshold and video
            cv2.imshow("threshold",thresh1)
            #write current number of fanning bees to current frame
            cv2.putText(img1, "Fanning Bees: {}".format(curFan), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            #draw every contour on the current frame for testing purposes
            #cv2.drawContours(img1, contours1, -1, (0,255,0), 2)
            cv2.imshow("contours",img1)
            
            #increment img2
            img1=img2
        else:    
            img1=img2
            img1=img1[75:75+315,0:0+637]
        key=cv2.waitKey(1) & 0xFF
        #if q is pressed, stop loop
        if key == ord("q"):
            break
        #time.sleep(1)
    make_vids(d_frames)
    #close all windows and video stream    
    vs.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()