import cv2
from ultralytics import YOLO
import threading
import time

class HandDetector:
    def __init__(self, model_name: str, model_path: str):
        
        self.name = model_name
        self._lock = threading.Lock()
        self._running = True

        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
        
        midpoint_x = self.frame_width//2
        
        prev_time = time.time()
        
        while self._running:
            try:
                success, frame = self.cap.read()
                if not success:
                    continue
                
                frame = frame[:, ::-1, :]
                
                result = self.model(frame, verbose=False, conf=0.5, imgsz=640)

                for box in result[0].boxes:
                    
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    
                    normalized_y = ((y1 + y2) / 2) / self.frame_height
                    if x1 < midpoint_x:
                        with self._lock:
                            self.latest_l_player_norm_y = normalized_y
                    else:
                        with self._lock:
                            self.latest_r_player_norm_y = normalized_y
                
                # Draw results on frame
                annotated_frame = result[0].plot()
                
                curr_time = time.time()
                fps_actual = 1 / (curr_time - prev_time)
                prev_time = curr_time
                
                # Add model name to frame
                cv2.putText(annotated_frame, self.name, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # Add FPS to frame
                cv2.putText(annotated_frame, f"FPS: {fps_actual:.2f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # Display frame
                cv2.imshow("Detection", annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.release()
                    break
                    
            except Exception as e:
                print(f"Error in hand detection loop: {e}")
                continue

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