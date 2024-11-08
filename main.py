import face_recognition
import os, sys
import cv2
import numpy as np
import math



def face_confidence(face_distance, face_match_threashold =0.6):
    f_range = (1.0 - face_match_threashold)
    linear_val = (1.0 - face_distance) / (f_range * 2.0)

    if face_distance > face_match_threashold:
        return str(round(linear_val * 100, 2)) + "%"
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"
        


class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()

    def encode_faces(self):
        for image in os.listdir('new_faces'):
            face_image = face_recognition.load_image_file(f'new_faces/{image}')
            encodings = face_recognition.face_encodings(face_image)

            if len(encodings) > 0:
                face_encoding = encodings[0]
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(image.split(".")[0])
        else:
            print(f"Warning: No faces found in {image}. Skipping this file.")

        print(self.known_face_names)

    def add_new_face(self,frame):
        name = input("Add a name for new user (firstName_lastName): ")

        image_path = f'new_faces/{name}.jpeg'

        cv2.imwrite(image_path, frame)

        face_image = face_recognition.load_image_file(image_path)
        face_encoding = face_recognition.face_encodings(face_image)[0]
        
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)
        print(f"Added new face: {name}")



    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit("Video source not found...")

        while True:
            ret, frame = (video_capture.read())
          

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
                

                # Find all faces in current frame
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)


                self.face_names = []

                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = 'Unkown'
                    confidence = 'Click T to add face'

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    self.face_names.append(f'{name} ({confidence})')

            self.process_current_frame = not self.process_current_frame

            # Display annotations

            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Face Recognition', frame)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            elif key == ord('t'):
                self.add_new_face(frame)

        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()