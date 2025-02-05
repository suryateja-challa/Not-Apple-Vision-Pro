import cv2
import numpy as np
import mediapipe as mp
import pyautogui as pg

pg.FAILSAFE = False

current_x, current_y = 240, 220

SMOOTHING_FACTOR = 0.7
smoothed_x, smoothed_y = current_x, current_y

pg.moveTo(current_x, current_y)

mp_face_mesh = mp.solutions.face_mesh

# LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
# RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

LEFT_IRIS = [469, 470, 471, 472]
RIGHT_IRIS = [474, 475, 476, 477]

cap = cv2.VideoCapture(0)

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as face_mesh:

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = face_mesh.process(frame)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        img_h, img_w = image.shape[:2]

        if results.multi_face_landmarks:
            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int) for p in results.multi_face_landmarks[0].landmark])

            # Marking the eyes
            # cv2.polylines(frame, [mesh_points[LEFT_EYE]], True, (0, 255, 0), 1, cv2.LINE_AA)
            # cv2.polylines(frame, [mesh_points[RIGHT_EYE]], True, (0, 255, 0), 1, cv2.LINE_AA)

            # Marking the iris
            # cv2.polylines(frame, [mesh_points[LEFT_IRIS]], True, (255, 0, 0), 1, cv2.LINE_AA)
            # cv2.polylines(frame, [mesh_points[RIGHT_IRIS]], True, (255, 0, 0), 1, cv2.LINE_AA)

            # Drawing circle around tracked iris
            # (l_cx, lcy), l_radius = cv2.minEnclosingCircle(mesh_points[LEFT_IRIS])
            # (r_cx, r_cy), r_radius = cv2.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            # center_left = np.array([l_cx, lcy], dtype=np.int32)
            # center_right = np.array([r_cx, r_cy], dtype=np.int32)
            # cv2.circle(image, center_left, int(l_radius), (0, 255, 0), 1, cv2.LINE_AA)
            # cv2.circle(image, center_right, int(r_radius), (0, 255, 0), 1, cv2.LINE_AA)

            # Storing location of pupils
            left_pupil_x, left_pupil_y = mesh_points[468]
            right_pupil_x, right_pupil_y = mesh_points[473]

            # Marking the pupils
            cv2.circle(image, mesh_points[468], 2, (0, 0, 255), 2, cv2.LINE_4)
            cv2.circle(image, mesh_points[473], 2, (0, 0, 255), 2, cv2.LINE_4)

            # Centroid of position of pupil
            x = (left_pupil_x + right_pupil_x) // 2
            y = (left_pupil_y + right_pupil_y) // 2

            smoothed_x = SMOOTHING_FACTOR * smoothed_x + (1 - SMOOTHING_FACTOR) * x
            smoothed_y = SMOOTHING_FACTOR * smoothed_y + (1 - SMOOTHING_FACTOR) * y

            scaling_factor = 20

            # pg.move((x - current_x) * scaling_factor, (y - current_y) * scaling_factor)
            # current_x, current_y = x, y

            pg.move(int(smoothed_x - current_x) * scaling_factor, int(smoothed_y - current_y) * scaling_factor)
            current_x, current_y = smoothed_x, smoothed_y

            # Position of centroid
            print("x={}, y={}".format(int(smoothed_x), int(smoothed_y)))

        cv2.imshow('Pupil Tracking', image)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()