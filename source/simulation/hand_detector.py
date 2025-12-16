import cv2
from ultralytics import YOLO
import threading
import time

class HandDetector:
    def __init__(self, model_name: str, model_path: str):
        
        self.name = model_name
        self._lock = threading.Lock()
        self._running = True

        # self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap = cv2.VideoCapture(0)
        self.model = YOLO(model_path)
        self.model_path = model_path
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)

        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        self.latest_l_player_norm_y = 0
        self.latest_r_player_norm_y = 0
        
    def detect_hands(self):
        """This function will run in a separate thread"""
        midpoint_x = self.frame_width // 2
        prev_time = time.time()

        try:
            while self._running:
                success, frame = self.cap.read()
                if not success:
                    continue
                # Mirror the frame
                frame = frame[:, ::-1, :]
                result = self.model(frame, verbose=False, conf=0.5, imgsz=640)
                for box in result[0].boxes:
                    # Extract coordinates, converting to int
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    normalized_y = ((y1 + y2) / 2) / self.frame_height
                    with self._lock:
                        if x1 < midpoint_x:
                            self.latest_l_player_norm_y = normalized_y
                        else:
                            self.latest_r_player_norm_y = normalized_y
                # Draw results on frame
                annotated_frame = result[0].plot()
                curr_time = time.time()
                fps_actual = 1 / (curr_time - prev_time)
                prev_time = curr_time
                cv2.putText(annotated_frame, self.name, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"FPS: {fps_actual:.2f}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("Detection", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self._running = False
                    break

        except Exception as e:
            print(f"Error in hand detection loop: {e}")


    def get_latest_left_player_y(self):
        with self._lock:
            return self.latest_l_player_norm_y
        
    def get_latest_right_player_y(self):
        with self._lock:
            return self.latest_r_player_norm_y
            
    def release(self):
        self._running = False
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detection = HandDetector(model_path='./model_training/runs/detect/hand_detection_11n/weights/best.pt', model_name="yolo11n")
    detection.detect_hands()