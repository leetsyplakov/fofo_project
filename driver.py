import cv2
import face_recognition
import numpy as np
import time
import datetime
import os
from send_email import email_send
import subprocess

the_now = datetime.datetime.now()
last_execution_time = None
camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'

qcd = cv2.QRCodeDetector()
cap = cv2.VideoCapture(camera_id)

FLAG_TAKE_PICTURE = False
FLAG_FOFO = False
FLAG_KNOWN_FACE = False
FLAG_UNKNOWN_FACE = False
FLAG_EMPTY_UNKNOWN_IMG_FLD = False

COUNTER = 0
KNOWN_FOLDER = 'known_img/'
UNKNOWN_FOLDER = 'unknown_img/'
EMAIL_RECEIVER = ''

if not os.path.exists(KNOWN_FOLDER):
    os.mkdir(KNOWN_FOLDER)
if not os.path.exists(UNKNOWN_FOLDER):
    os.mkdir(UNKNOWN_FOLDER)

# def setup_email(s):
#     EMAIL_RECEIVER = str(s).split(' ')[1]



def reset_memory():
    import shutil
    shutil.rmtree(UNKNOWN_FOLDER)
    os.mkdir(UNKNOWN_FOLDER)
    shutil.rmtree(KNOWN_FOLDER)
    os.mkdir(KNOWN_FOLDER)

def four_long_blinks(cap,camera_id):
    cap.release()
    time.sleep(1)
    cap = cv2.VideoCapture(camera_id)
    cap.release()
    time.sleep(1)
    cap = cv2.VideoCapture(camera_id)
    cap.release()
    time.sleep(1)
    cap = cv2.VideoCapture(camera_id)
    cap.release()
    time.sleep(1)
    cap = cv2.VideoCapture(camera_id)
    return cap

def three_camera_blinks(cap,camera_id):
    cap.release()
    cap = cv2.VideoCapture(camera_id)
    cap.release()
    cap = cv2.VideoCapture(camera_id)
    cap.release()
    cap = cv2.VideoCapture(camera_id)
    return cap

def take_picture(frame,fp):

    cv2.imwrite(filename=fp, img=frame)
    print(f'SAVED: {fp}')

def encode_face(fn):
    return face_recognition.face_encodings(face_recognition.load_image_file(fn))[0]

def is_any_match(lst):
    for i in lst:
        if i == True:
            return i
    return False


print('STARTING THE WHILE LOOP')
while True:
    ret, frame = cap.read()

    if ret:
        ret_qr, decoded_info, points, _ = qcd.detectAndDecodeMulti(frame)
        if ret_qr:
            for s, p in zip(decoded_info, points):
                if s:
                    print(f'QR-Code command detected {s}')
                    if s == 'TakePicture':
                        FLAG_TAKE_PICTURE = True
                        FLAG_FOFO = False
                        FLAG_KNOWN_FACE = False
                        FLAG_UNKNOWN_FACE = False

                        cap = three_camera_blinks(cap, camera_id)
                    if s == 'DetectUnknownFace':
                        FLAG_TAKE_PICTURE = False
                        FLAG_FOFO = True
                        FLAG_KNOWN_FACE = False
                        FLAG_UNKNOWN_FACE = True
                        cap = three_camera_blinks(cap,camera_id)
                    if s == 'DetectKnownFace':
                        FLAG_TAKE_PICTURE = False
                        FLAG_FOFO = True
                        FLAG_KNOWN_FACE = True
                        FLAG_UNKNOWN_FACE = False
                        cap = three_camera_blinks(cap,camera_id)
                    if s == 'MemoryReset':
                        FLAG_TAKE_PICTURE = False
                        FLAG_FOFO = False
                        FLAG_KNOWN_FACE = False
                        FLAG_UNKNOWN_FACE = False
                        cap = three_camera_blinks(cap, camera_id)
                        reset_memory()
                    if str(s).startswith('SetupWifi '):
                        FLAG_TAKE_PICTURE = False
                        FLAG_FOFO = False
                        FLAG_KNOWN_FACE = False
                        FLAG_UNKNOWN_FACE = False
                        try:
                            if os.platform.system() == 'Darwin':
                                s = str(s).split(' ')
                                cmd = f'networksetup -setairportnetwork en0 {s[1]} {s[2]}'
                                subprocess.check_output(cmd, shell=True)
                                cap = three_camera_blinks(cap, camera_id)
                            else:
                                s = str(s).split(' ')
                                cmd = f'nmcli dev wifi connect {s[1]} password {s[2]}'
                                subprocess.check_output(cmd, shell=True)
                                cap = three_camera_blinks(cap, camera_id)
                            print('WiFi Configured')
                        except Exception as e:
                            print(e)
                            cap = four_long_blinks(cap,camera_id)
                    if str(s).startswith('SetupEmailReceiver '):
                        FLAG_TAKE_PICTURE = False
                        FLAG_FOFO = False
                        FLAG_KNOWN_FACE = False
                        FLAG_UNKNOWN_FACE = False
                        os.environ['FOFO_EMR'] = str(s).split(' ')[1]
                        print(f'Receiver email setup')
                        cap = three_camera_blinks(cap, camera_id)
                    if str(s).startswith('SetupEmailSender '):
                        FLAG_TAKE_PICTURE = False
                        FLAG_FOFO = False
                        FLAG_KNOWN_FACE = False
                        FLAG_UNKNOWN_FACE = False
                        try:
                            cmd = str(s).split(' ')
                            os.environ['FOFO_GMAIL'] = cmd[1]
                            os.environ['FOFO_GMAIL_PWD'] = cmd[2]
                            print(f'Sender email setup complete')
                        except Exception as e:
                            print(e)
                        cap = three_camera_blinks(cap, camera_id)

    # if cv2.waitKey(delay) & 0xFF == ord('q'):
    #     break

    if FLAG_TAKE_PICTURE:
        print(COUNTER)
        if COUNTER % 5 ==0:
            cap.release()
            cap = cv2.VideoCapture(camera_id)

        if COUNTER == 25:
            the_now = datetime.datetime.now()
            fp = f'known_img/saved_img_{the_now}.jpg'
            take_picture(frame,fp)
            FLAG_TAKE_PICTURE = False
            COUNTER = 0
            cap.release()
            cap = cv2.VideoCapture(camera_id)
            last_execution_time = the_now
            email_send(fp,s)
        COUNTER += 1

    if FLAG_FOFO:
        try:
            match_index = -1
            dir = os.listdir(KNOWN_FOLDER)
            if len(dir) != 0:
                known_face_encodings = [encode_face(KNOWN_FOLDER + f) for f in os.listdir(KNOWN_FOLDER)
                                        if os.path.isfile(os.path.join(KNOWN_FOLDER, f)) and f != '.DS_Store']
            else:
                print('No known images available, please take picture first')
                FLAG_FOFO = False
                FLAG_KNOWN_FACE = False
                FLAG_UNKNOWN_FACE = False
                cap = four_long_blinks(cap,camera_id)

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                print(f'Is any match? {is_any_match(matches)}')
                if not is_any_match(matches):
                    print('Unknown face detected')
                    dir = os.listdir(UNKNOWN_FOLDER)
                    if len(dir) != 0:
                        unknown_face_encodings = [encode_face(UNKNOWN_FOLDER + f) for f in os.listdir(UNKNOWN_FOLDER)
                                                  if os.path.isfile(os.path.join(UNKNOWN_FOLDER, f)) and f != '.DS_Store']
                        matches = face_recognition.compare_faces(unknown_face_encodings, face_encoding)

                        if not is_any_match(matches):
                            print('Anther unknown face detected')
                            the_now = datetime.datetime.now()
                            fp = f'unknown_img/saved_img_{the_now}.jpg'
                            take_picture(frame, fp)
                            if FLAG_UNKNOWN_FACE:
                                email_send(fp, s)
                                print(f'SEND EMAIL - UNKNOWN FACE DETECTED: {fp}')
                        else:
                            print('The unknown face is already in the system')

                    else:
                        print('The first unknown face detected')
                        the_now = datetime.datetime.now()
                        fp = f'unknown_img/saved_img_{the_now}.jpg'
                        take_picture(frame, fp)
                        if FLAG_UNKNOWN_FACE:
                            print(f'SEND EMAIL - UNKNOWN FACE DETECTED: {fp}')
                            email_send(fp, s)


                else:
                    print('A KNOW FACE DETECTED')
                    if FLAG_KNOWN_FACE:
                        email_send(fp, s)
        except:
            pass

#cv2.destroyWindow(window_name)




