import cv2
from cv_bridge import CvBridge

class ArucoTargetDetector:
    def __init__(self):
        self.bridge = CvBridge()
        
        self.dict_primary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
        self.dict_fallback = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        
        # Configure advanced tracking parameters to prevent silent drops
        self.aruco_params = cv2.aruco.DetectorParameters()
        self.aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        self.aruco_params.errorCorrectionRate = 0.6
        
        self.focal_length_px = 550.0  
        self.marker_real_width_m = 0.05  

    def process_frame(self, image_msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(image_msg, desired_encoding='bgr8')
        except Exception as e:
            print(f"❌ [Vision Debug] Bridge Error: {e}")
            return None, None, None

        # Try parsing with both possible API layouts using our sharp-edge configuration
        try:
            detector_1000 = cv2.aruco.ArucoDetector(self.dict_primary, self.aruco_params)
            corners, ids, rejected = detector_1000.detectMarkers(cv_image)
            
            if ids is None or len(ids) == 0:
                detector_50 = cv2.aruco.ArucoDetector(self.dict_fallback, self.aruco_params)
                corners, ids, rejected = detector_50.detectMarkers(cv_image)
        except AttributeError:
            corners, ids, rejected = cv2.aruco.detectMarkers(cv_image, self.dict_primary, parameters=self.aruco_params)
            if ids is None or len(ids) == 0:
                corners, ids, rejected = cv2.aruco.detectMarkers(cv_image, self.dict_fallback, parameters=self.aruco_params)

        if ids is not None and len(ids) > 0:
            target_id = int(ids[0][0])
            print(f"🎯 [Vision Debug] OPENCV SAW MARKER! ID: {target_id}")
            marker_corners = corners[0][0]
            top_left_x = marker_corners[0][0]
            top_right_x = marker_corners[1][0]
            
            pixel_width = abs(top_right_x - top_left_x)
            center_x = (top_left_x + top_right_x) / 2.0
            image_center_x = cv_image.shape[1] / 2.0
            offset_x = center_x - image_center_x
            
            if pixel_width > 0:
                distance = (self.marker_real_width_m * self.focal_length_px) / pixel_width
            else:
                distance = float('inf')
                
            return target_id, distance, offset_x
            
        return None, None, None