import numpy as np
import cv2

class ShootingAnalyzer:
  def __init__(self, SHOOTING_ARM="RIGHT", delta_t=1/30):
    self.SHOOTING_ARM = SHOOTING_ARM
    self.delta_t = delta_t
    self.shot_completed = False
    # main metrics extracted
    self.metrics = {
      "Setup": {
        "total_knee_bend": 0,
        "avg_knee_bend": float("inf"),
        "max_knee_bend": float("inf"),
        "total_body_lean": 0,
        "avg_body_lean": float("inf"),
        "max_body_lean": 0,
        "min_body_lean": float("inf"),
        "frame_count": 0,
        "stored": False
      },
      "Release": {
        "total_hip_angle": 0,
        "avg_hip_angle": float("inf"),
        "total_knee_bend": 0,
        "avg_knee_bend": float("inf"),
        "total_elbow_angle": 0,
        "avg_elbow_angle": float("inf"),
        "max_wrist_height": 0,
        "avg_knee_velocity": 0,
        "frame_count": 0,
        "stored": False
      },
      "Follow-through": {
        "release_angle": -1,
        "elbow_above_eye": -1,
        "body_lean_angle": -1,
        "hip_angle": -1,
        "knee_angle": -1,
        "stored": False
      }
    }
    # variables for phase detection
    self.current_phase = "Null"
    self.release_detected = False
    self.release_angle = None
    self.allow_follow_through = False
    self.previous_knee_angle = None
    self.knee_velocities = []
    self.shot_ended = False

  # calculates the angle of a joint from points a, b ,c
  def calculate_angle(self, a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))

    return np.degrees(angle)
  
  # calculates the angle of the shoulder, relative to the body. - if behind, + if in front
  def calculate_shoulder_angle(self, hip, shoulder, elbow):
    base_angle = self.calculate_angle(hip, shoulder, elbow)

    shoulder_hip_vector = np.array([hip.x - shoulder.x, hip.y - shoulder.y])
    shoulder_elbow_vector = np.array([elbow.x - shoulder.x, elbow.y - shoulder.y])

    cross_product_z = np.cross(shoulder_hip_vector, shoulder_elbow_vector)

    if cross_product_z < 0 and self.SHOOTING_ARM == "RIGHT":
      return base_angle
    elif cross_product_z < 0 and self.SHOOTING_ARM == "LEFT":
      return -base_angle
    elif cross_product_z > 0 and self.SHOOTING_ARM == "LEFT":
      return base_angle
    else:
      return -base_angle
  
  # calculates the angle of the body lean relative to the y axis
  def calculate_body_lean(self, shoulder, hip):
    dx = shoulder.x - hip.x
    dy = shoulder.y - hip.y

    angle_radians = np.arctan2(dx, -dy)
    angle_degrees = np.degrees(angle_radians)

    if self.SHOOTING_ARM == "RIGHT":
      return angle_degrees
    else:
      return -angle_degrees
  
  # calculates the angle of the wrist
  def calculate_wrist_angle(self, elbow, wrist, index_finger):
    wrist_point = np.array([wrist.x, wrist.y])
    index_point = np.array([index_finger.x, index_finger.y])
    elbow_point = np.array([elbow.x, elbow.y])

    wrist_elbow_vector = wrist_point - elbow_point
    wrist_index_vector = index_point - wrist_point

    dot_product = np.dot(wrist_elbow_vector, wrist_index_vector)
    magnitude_product = np.linalg.norm(wrist_elbow_vector) * np.linalg.norm(wrist_index_vector)
    cosine_angle = np.clip(dot_product / magnitude_product, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))

    cross_product_z = np.cross(wrist_elbow_vector, wrist_index_vector)

    if self.SHOOTING_ARM == "RIGHT":
        if cross_product_z < 0:  # Palm is bent backward
            return 180 - angle
        else:  # Palm is bent forward
            return 180 + angle
    elif self.SHOOTING_ARM == "LEFT":
        if cross_product_z > 0:  # Palm is bent backward for the left hand
            return 180 - angle
        else:  # Palm is bent forward for the left hand
            return 180 + angle
  
  # calculates the height of wrist relative to the eye, normalized to torso length
  def calculate_wrist_height(self, wrist, eye, shoulder, hip):
    torso_length = abs(shoulder.y - hip.y)
    
    wrist_eye_diff = eye.y - wrist.y
    normalized = wrist_eye_diff / torso_length if torso_length != 0 else 0

    return normalized * 10
  
  # calculates the height of elbow relative to the eye, normalized to torso length
  def calculate_elbow_eye_height(self, elbow, eye, shoulder, hip):
    torso_length = abs(shoulder.y - hip.y)
    elbow_eye_diff = eye.y - elbow.y

    normalized = elbow_eye_diff / torso_length if torso_length != 0 else 0

    return normalized * 100
  
  # detect what phase the shooter is currently in
  def detect_phase(self, angles, landmarks):
    if self.current_phase == "Complete":
      return self.current_phase

    elbow_angle = angles['elbow']
    wrist_angle = angles['wrist']
    shoulder_angle = angles['shoulder']
    knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
    body_lean = angles['body_lean']
    hip_angle = angles['hip_angle']

    # NULL phase
    if self.current_phase == "Null":
      self.allow_follow_through = False
      if self.shot_completed is False:
        # change to setup
        if shoulder_angle < 45 and elbow_angle < 135 and knee_angle < 170 and shoulder_angle > 6:
          self.current_phase = "Setup"
          self.release_detected = False
    
    # SETUP phase
    elif self.current_phase == "Setup":
      # set metrics to setup
      setup_metrics = self.metrics["Setup"]
      
      setup_metrics["max_knee_bend"] = min(setup_metrics["max_knee_bend"], knee_angle)
      setup_metrics["min_body_lean"] = min(setup_metrics["min_body_lean"], body_lean)
      setup_metrics["max_body_lean"] = max(setup_metrics["max_body_lean"], body_lean)
      setup_metrics["total_knee_bend"] += knee_angle
      setup_metrics["total_body_lean"] += body_lean
      
      setup_metrics["frame_count"] += 1

      # change to release
      if elbow_angle < 100 and shoulder_angle > 60 and elbow_angle > 70:
        self.current_phase = "Release"
        self.release_detected = False

        # setup finished, store setup metrics
        if not setup_metrics["stored"] and setup_metrics["frame_count"] > 0:
          setup_metrics["avg_knee_bend"] = setup_metrics["total_knee_bend"] / setup_metrics["frame_count"]
          setup_metrics["avg_body_lean"] = setup_metrics["total_body_lean"] / setup_metrics["frame_count"]
        setup_metrics["stored"] = True
    
    # RELEASE phase
    elif self.current_phase == "Release":
      # set metrics to release
      release_metrics = self.metrics["Release"]
      follow_through_metrics = self.metrics["Follow-through"]
      
      release_metrics["total_hip_angle"] += hip_angle
      release_metrics["total_knee_bend"] += knee_angle
      release_metrics["total_elbow_angle"] += elbow_angle
      release_metrics["max_wrist_height"] = max(
        release_metrics["max_wrist_height"], 
        self.calculate_wrist_height(landmarks["wrist"], landmarks["eye"], landmarks["shoulder"], landmarks["hip"])
      )
      if self.previous_knee_angle is not None:
        knee_velocity = (knee_angle - self.previous_knee_angle) / self.delta_t
        self.knee_velocities.append(knee_velocity) 

      self.previous_knee_angle = knee_angle

      release_metrics["frame_count"] += 1

      if elbow_angle > 125:
        self.allow_follow_through = True

      # change to follow-through
      if (elbow_angle > 160 and shoulder_angle > 130 and self.allow_follow_through) or (wrist_angle > 175 and elbow_angle > 140):
        self.release_detected = True
        self.current_phase = "Follow-through"
        self.allow_follow_through = False

        # release finished, store release metrics
        if not release_metrics["stored"] and release_metrics["frame_count"] > 0:
          release_metrics["avg_hip_angle"] = release_metrics["total_hip_angle"] / release_metrics["frame_count"]
          release_metrics["avg_knee_bend"] = release_metrics["total_knee_bend"] / release_metrics["frame_count"]
          release_metrics["avg_elbow_angle"] = release_metrics["total_elbow_angle"] / release_metrics["frame_count"]
          release_metrics["avg_knee_velocity"] = np.mean(self.knee_velocities) if self.knee_velocities else 0
        release_metrics["stored"] = True

        # store follow through metrics
        if not follow_through_metrics["stored"]:
          follow_through_metrics["release_angle"] = int(shoulder_angle-90)
          follow_through_metrics["elbow_above_eye"] = self.calculate_elbow_eye_height(
            landmarks['elbow'], landmarks['eye'], landmarks['shoulder'], landmarks['hip']
          )
          follow_through_metrics["body_lean_angle"] = body_lean
          follow_through_metrics["hip_angle"] = hip_angle
          follow_through_metrics["knee_angle"] = knee_angle
        follow_through_metrics["stored"] = True

    # FOLLOW-THROUGH phase
    elif self.current_phase == "Follow-through":
      self.shot_completed = True

      # change to null
      if shoulder_angle < 120 and elbow_angle < 180:
        self.current_phase = "Complete"
        self.allow_follow_through = False
        self.shot_ended = True
    
    return self.current_phase
  
  def reset_metrics(self):
    self.__init__(self.SHOOTING_ARM, self.delta_t)
    self.shot_completed = False
  
  def display_debug_metrics(self, frame, angles, phase):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_color = (255, 255, 255)
    start_x, start_y = 10, 30
    line_height = 30

    # display phase
    cv2.putText(frame, f"Current Phase: {phase}", (start_x, start_y), font, 0.8, text_color, 2)
    start_y += line_height

    for angle_name, angle_value in angles.items():
      cv2.putText(
        frame,
        f'{angle_name.replace("_", " ").capitalize()}: {int(angle_value)}',
        (start_x, start_y),
        font,
        0.6,
        text_color,
        2
      )
      start_y += line_height

  def display_metrics(self, frame):
    positions = {
      "Setup": (350, 70),
      "Release": (650, 70),
      "Follow-through": (950, 70)
    }
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0, 0, 255) # red

    for phase, metrics_data in self.metrics.items():
      x, y = positions[phase]
      
      cv2.putText(frame, phase, (x, y), font, 0.8, color, 2)
      y += 30
      if phase == "Setup" and metrics_data["stored"]:
        metrics_list = [
          f"Total frame count: {metrics_data['frame_count']}",
          f"Avg Knee Bend: {metrics_data['avg_knee_bend']:.02f}",
          f"Max Knee Bend: {metrics_data['max_knee_bend']:.02f}",
          f"Avg Body Lean: {metrics_data['avg_body_lean']:.02f}",
          f"Max Body Lean: {metrics_data['max_body_lean']:.02f}",
          f"Min Body Lean: {metrics_data['min_body_lean']:.02f}"
        ]
      elif phase == "Release" and metrics_data["stored"]:
        metrics_list = [
          f"Total frame count: {metrics_data['frame_count']}",
          f"Avg Hip Angle: {metrics_data['avg_hip_angle']:.02f}",
          f"Avg Knee Bend: {metrics_data['avg_knee_bend']:.02f}",
          f"Avg Elbow Angle: {metrics_data['avg_elbow_angle']:.02f}",
          f"Max Wrist Height: {metrics_data['max_wrist_height']:.02f}",
          f"Avg Knee Velocity: {metrics_data['avg_knee_velocity']:.02f} d/s"
        ]
      elif phase == "Follow-through" and metrics_data["stored"]:
        metrics_list = [
          f"Release Angle: {metrics_data['release_angle']}",
          f"Elbow Above Eye: {metrics_data['elbow_above_eye']:.02f}",
          f"Hip Angle: {metrics_data['hip_angle']:.02f}",
          f"Knee Angle: {metrics_data['knee_angle']:.02f}",
          f"Body Lean Angle: {metrics_data['body_lean_angle']:.02f}"
        ]
      else:
        metrics_list = []
      
      for metric in metrics_list:
        cv2.putText(frame, metric, (x, y), font, 0.6, color, 2)
        y += 30