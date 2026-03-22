import numpy as np
import cv2


class ShootingAnalyzer:
    """Shot phase/metric analyzer used by the backend video pipeline."""

    PHASE_NULL = "Null"
    PHASE_SETUP = "Setup"
    PHASE_RELEASE = "Release"
    PHASE_FOLLOW_THROUGH = "Follow-through"
    PHASE_COMPLETE = "Complete"

    ARM_RIGHT = "RIGHT"
    ARM_LEFT = "LEFT"

    FOLLOW_THROUGH_MAX_FRAMES = 35

    def __init__(self, SHOOTING_ARM="RIGHT", delta_t=1 / 30):
        self.SHOOTING_ARM = SHOOTING_ARM
        self.delta_t = delta_t
        self.shot_completed = False

        self.follow_through_frame_count = 0
        self.metrics = self._create_metrics_template()

        # variables for phase detection
        self.current_phase = self.PHASE_NULL
        self.release_detected = False
        self.release_angle = None
        self.allow_follow_through = False
        self.previous_knee_angle = None
        self.previous_shoulder_angle = None
        self.knee_velocities = []
        self.shot_ended = False

    def _create_metrics_template(self):
        """Return fresh metrics structure for all phases."""
        return {
            self.PHASE_SETUP: {
                "total_knee_bend": 0,
                "avg_knee_bend": float("inf"),
                "max_knee_bend": float("inf"),
                "total_body_lean": 0,
                "avg_body_lean": float("inf"),
                "max_body_lean": 0,
                "min_body_lean": float("inf"),
                "total_head_tilt": 0,
                "avg_head_tilt": float("inf"),
                "total_elbow_angle": 0,
                "avg_elbow_angle": float("inf"),
                "frame_count": 0,
                "stored": False,
            },
            self.PHASE_RELEASE: {
                "total_hip_angle": 0,
                "avg_hip_angle": float("inf"),
                "total_knee_bend": 0,
                "avg_knee_bend": float("inf"),
                "total_elbow_angle": 0,
                "avg_elbow_angle": float("inf"),
                "max_wrist_height": 0,
                "total_shoulder_angle": 0,
                "avg_shoulder_angle": float("inf"),
                "total_head_tilt": 0,
                "avg_head_tilt": float("inf"),
                "total_body_lean": 0,
                "avg_body_lean": float("inf"),
                "total_forearm_deviation": 0,
                "avg_forearm_deviation": float("inf"),
                "max_setpoint": float("inf"),
                "frame_count": 0,
                "stored": False,
            },
            self.PHASE_FOLLOW_THROUGH: {
                "release_angle": -1,
                "elbow_above_eye": -1,
                "body_lean_angle": -1,
                "hip_angle": -1,
                "knee_angle": -1,
                "head_tilt": -1,
                "frame_count": 0,
                "stored": False,
            },
        }

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

        if cross_product_z < 0 and self.SHOOTING_ARM == self.ARM_RIGHT:
            return base_angle
        elif cross_product_z < 0 and self.SHOOTING_ARM == self.ARM_LEFT:
            return -base_angle
        elif cross_product_z > 0 and self.SHOOTING_ARM == self.ARM_LEFT:
            return base_angle
        else:
            return -base_angle

    # calculates the head tilt angle
    def calculate_head_angle(self, eye, ear):
        dx = eye.x - ear.x
        dy = eye.y - ear.y

        angle_rad = np.arctan2(dy, dx)
        head_angle = -np.degrees(angle_rad)
        return head_angle

    # calculates the angle of the body lean relative to the y axis
    def calculate_body_lean(self, shoulder, hip):
        dx = shoulder.x - hip.x
        dy = shoulder.y - hip.y

        angle_radians = np.arctan2(dx, -dy)
        angle_degrees = np.degrees(angle_radians)

        if self.SHOOTING_ARM == self.ARM_RIGHT:
            return angle_degrees
        else:
            return -angle_degrees

    def calculate_forearm_alignment(self, elbow, wrist):
        dx = wrist.x - elbow.x
        dy = wrist.y - elbow.y

        angle_rad = np.arctan2(dx, -dy)
        out = np.degrees(angle_rad)

        if self.SHOOTING_ARM == self.ARM_RIGHT:
            return out
        else:
            return -out

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

        if self.SHOOTING_ARM == self.ARM_RIGHT:
            if cross_product_z < 0:  # Palm is bent backward
                return 180 - angle
            else:  # Palm is bent forward
                return 180 + angle
        elif self.SHOOTING_ARM == self.ARM_LEFT:
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

        return (elbow_eye_diff * 1000) / 2

    def calculate_release_setpoint(self, index_finger, eye):
        x_index_finger = index_finger.x
        x_eye = eye.x

        if self.SHOOTING_ARM == self.ARM_RIGHT:
            diff = x_index_finger - x_eye
        else:
            diff = x_eye - x_index_finger

        out = (diff * 1000) / 2
        return out

    def _accumulate_setup_metrics(self, knee_angle, body_lean, head_tilt, elbow_angle):
        setup_metrics = self.metrics[self.PHASE_SETUP]
        setup_metrics["max_knee_bend"] = min(setup_metrics["max_knee_bend"], knee_angle)
        setup_metrics["min_body_lean"] = min(setup_metrics["min_body_lean"], body_lean)
        setup_metrics["max_body_lean"] = max(setup_metrics["max_body_lean"], body_lean)
        setup_metrics["total_knee_bend"] += knee_angle
        setup_metrics["total_body_lean"] += body_lean
        setup_metrics["total_head_tilt"] += head_tilt
        setup_metrics["total_elbow_angle"] += elbow_angle

    def _accumulate_release_metrics(self, hip_angle, knee_angle, elbow_angle, shoulder_angle, head_tilt, body_lean, forearm_deviation, landmarks):
        release_metrics = self.metrics[self.PHASE_RELEASE]
        release_metrics["total_hip_angle"] += hip_angle
        release_metrics["total_knee_bend"] += knee_angle
        release_metrics["total_elbow_angle"] += elbow_angle
        release_metrics["total_shoulder_angle"] += shoulder_angle
        release_metrics["total_head_tilt"] += head_tilt
        release_metrics["total_body_lean"] += body_lean
        release_metrics["total_forearm_deviation"] += forearm_deviation
        release_metrics["max_wrist_height"] = max(
            release_metrics["max_wrist_height"],
            self.calculate_wrist_height(landmarks["wrist"], landmarks["eye"], landmarks["shoulder"], landmarks["hip"]),
        )
        release_metrics["max_setpoint"] = min(
            release_metrics["max_setpoint"],
            self.calculate_release_setpoint(landmarks["index_finger"], landmarks["eye"]),
        )

    def _finalize_setup_metrics(self):
        setup_metrics = self.metrics[self.PHASE_SETUP]
        if not setup_metrics["stored"] and setup_metrics["frame_count"] > 0:
            num_frames = setup_metrics["frame_count"]
            setup_metrics["avg_knee_bend"] = setup_metrics["total_knee_bend"] / num_frames
            setup_metrics["avg_body_lean"] = setup_metrics["total_body_lean"] / num_frames
            setup_metrics["avg_head_tilt"] = setup_metrics["total_head_tilt"] / num_frames
            setup_metrics["avg_elbow_angle"] = setup_metrics["total_elbow_angle"] / num_frames
        setup_metrics["stored"] = True

    def _finalize_release_metrics(self):
        release_metrics = self.metrics[self.PHASE_RELEASE]
        if not release_metrics["stored"] and release_metrics["frame_count"] > 0:
            num_frames = release_metrics["frame_count"]
            release_metrics["avg_hip_angle"] = release_metrics["total_hip_angle"] / num_frames
            release_metrics["avg_knee_bend"] = release_metrics["total_knee_bend"] / num_frames
            release_metrics["avg_elbow_angle"] = release_metrics["total_elbow_angle"] / num_frames
            release_metrics["avg_shoulder_angle"] = (release_metrics["total_shoulder_angle"] / num_frames) - 90
            release_metrics["avg_head_tilt"] = release_metrics["total_head_tilt"] / num_frames
            release_metrics["avg_body_lean"] = release_metrics["total_body_lean"] / num_frames
            release_metrics["avg_forearm_deviation"] = release_metrics["total_forearm_deviation"] / num_frames
        release_metrics["stored"] = True

    def _store_follow_through_metrics(self, shoulder_angle, body_lean, hip_angle, knee_angle, head_tilt, landmarks):
        follow_through_metrics = self.metrics[self.PHASE_FOLLOW_THROUGH]
        if not follow_through_metrics["stored"]:
            follow_through_metrics["release_angle"] = int(shoulder_angle - 90 - body_lean)
            follow_through_metrics["elbow_above_eye"] = self.calculate_elbow_eye_height(landmarks["elbow"], landmarks["eye"], landmarks["shoulder"], landmarks["hip"])
            follow_through_metrics["body_lean_angle"] = body_lean
            follow_through_metrics["hip_angle"] = hip_angle
            follow_through_metrics["knee_angle"] = knee_angle
            follow_through_metrics["head_tilt"] = head_tilt
        follow_through_metrics["stored"] = True

    def _handle_null_phase(self, shoulder_angle, elbow_angle, knee_angle, head_tilt, body_lean, forearm_deviation):
        self.allow_follow_through = False

        if self.shot_completed is False:
            optimal = (
                shoulder_angle < 45
                and elbow_angle < 135
                and knee_angle < 170
                and shoulder_angle > 3
                and head_tilt > 10
                and head_tilt < 100
                and forearm_deviation < 100
                and forearm_deviation > 0
            )

            non_optimal = False
            if self.previous_shoulder_angle is not None:
                non_optimal = (
                    head_tilt > 10
                    and head_tilt < 100
                    and shoulder_angle > 5
                    and shoulder_angle < 60
                    and elbow_angle < 150
                    and forearm_deviation < 100
                    and forearm_deviation > 0
                    and (shoulder_angle - 3 > self.previous_shoulder_angle)
                )

            if optimal or non_optimal:
                self.current_phase = self.PHASE_SETUP
                self.release_detected = False
                self._accumulate_setup_metrics(knee_angle, body_lean, head_tilt, elbow_angle)

        self.previous_shoulder_angle = shoulder_angle

    def _handle_setup_phase(self, elbow_angle, shoulder_angle, knee_angle, forearm_deviation, hip_angle, head_tilt, body_lean, landmarks):
        setup_metrics = self.metrics[self.PHASE_SETUP]
        setup_metrics["frame_count"] += 1

        should_transition_to_release = (
            (elbow_angle < 110 and shoulder_angle > 70 and elbow_angle > 70 and knee_angle > 150)
            or (knee_angle > 170 and elbow_angle > 65 and shoulder_angle > 45 and forearm_deviation < 20)
            or (shoulder_angle > 85 and elbow_angle > 80 and elbow_angle < 140)
        )

        if should_transition_to_release:
            self.current_phase = self.PHASE_RELEASE
            self.release_detected = False

            if not setup_metrics["stored"] and setup_metrics["frame_count"] > 0:
                self._finalize_setup_metrics()
                self._accumulate_release_metrics(
                    hip_angle,
                    knee_angle,
                    elbow_angle,
                    shoulder_angle,
                    head_tilt,
                    body_lean,
                    forearm_deviation,
                    landmarks,
                )

            setup_metrics["stored"] = True
        else:
            self._accumulate_setup_metrics(knee_angle, body_lean, head_tilt, elbow_angle)

    def _handle_release_phase(self, elbow_angle, shoulder_angle, knee_angle, wrist_angle, hip_angle, head_tilt, body_lean, forearm_deviation, landmarks):
        release_metrics = self.metrics[self.PHASE_RELEASE]
        release_metrics["frame_count"] += 1

        should_transition_to_follow_through = (
            (elbow_angle > 163 and shoulder_angle > 130 and self.allow_follow_through and wrist_angle > 160)
            or (
                wrist_angle > 174
                and elbow_angle > 148
                and shoulder_angle > 120
                and knee_angle > 165
                and self.allow_follow_through
            )
            or (elbow_angle > 170 and shoulder_angle > 120 and self.allow_follow_through)
        )

        if should_transition_to_follow_through:
            self.release_detected = True
            self.current_phase = self.PHASE_FOLLOW_THROUGH
            self.allow_follow_through = False

            self._finalize_release_metrics()
            self._store_follow_through_metrics(
                shoulder_angle,
                body_lean,
                hip_angle,
                knee_angle,
                head_tilt,
                landmarks,
            )
        else:
            self._accumulate_release_metrics(
                hip_angle,
                knee_angle,
                elbow_angle,
                shoulder_angle,
                head_tilt,
                body_lean,
                forearm_deviation,
                landmarks,
            )

        if elbow_angle > 130:
            self.allow_follow_through = True

    def _handle_follow_through_phase(self, shoulder_angle, elbow_angle):
        self.shot_completed = True
        self.follow_through_frame_count += 1

        if (
            (shoulder_angle < 120 and elbow_angle < 180)
            or self.follow_through_frame_count >= self.FOLLOW_THROUGH_MAX_FRAMES
        ):
            follow_through_metrics = self.metrics[self.PHASE_FOLLOW_THROUGH]
            follow_through_metrics["frame_count"] = self.follow_through_frame_count
            self.current_phase = self.PHASE_COMPLETE
            self.allow_follow_through = False
            self.shot_ended = True

    # detect what phase the shooter is currently in
    def detect_phase(self, angles, landmarks):
        if self.current_phase == self.PHASE_COMPLETE:
            return self.current_phase

        elbow_angle = angles["elbow"]
        wrist_angle = angles["wrist"]
        shoulder_angle = angles["shoulder"]
        knee_angle = angles["dominant_knee"]
        body_lean = angles["body_lean"]
        hip_angle = angles["hip_angle"]
        head_tilt = angles["head_tilt"]
        forearm_deviation = angles["forearm_alignment"]

        if self.current_phase == self.PHASE_NULL:
            self._handle_null_phase(shoulder_angle, elbow_angle, knee_angle, head_tilt, body_lean, forearm_deviation)
        elif self.current_phase == self.PHASE_SETUP:
            self._handle_setup_phase(elbow_angle, shoulder_angle, knee_angle, forearm_deviation, hip_angle, head_tilt, body_lean, landmarks)
        elif self.current_phase == self.PHASE_RELEASE:
            self._handle_release_phase(elbow_angle, shoulder_angle, knee_angle, wrist_angle, hip_angle, head_tilt, body_lean, forearm_deviation, landmarks)
        elif self.current_phase == self.PHASE_FOLLOW_THROUGH:
            self._handle_follow_through_phase(shoulder_angle, elbow_angle)

        return self.current_phase

    def reset_metrics(self):
        self.__init__(self.SHOOTING_ARM, self.delta_t)
        self.shot_completed = False

    def display_debug_metrics(self, frame, angles, phase):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_color = (255, 255, 255)
        start_x, start_y = 10, 30
        line_height = 30

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
                2,
            )
            start_y += line_height

    def display_metrics(self, frame):
        positions = {
            self.PHASE_SETUP: (350, 70),
            self.PHASE_RELEASE: (650, 70),
            self.PHASE_FOLLOW_THROUGH: (950, 70),
        }
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (0, 0, 255)  # red

        for phase, metrics_data in self.metrics.items():
            x, y = positions[phase]

            cv2.putText(frame, phase, (x, y), font, 0.8, color, 2)
            y += 30

            if phase == self.PHASE_SETUP and metrics_data["stored"]:
                metrics_list = [
                    f"Total frame count: {metrics_data['frame_count']}",
                    f"Avg Knee Bend: {metrics_data['avg_knee_bend']:.02f}",
                    f"Max Knee Bend: {metrics_data['max_knee_bend']:.02f}",
                    f"Avg Body Lean: {metrics_data['avg_body_lean']:.02f}",
                    f"Max Body Lean: {metrics_data['max_body_lean']:.02f}",
                    f"Min Body Lean: {metrics_data['min_body_lean']:.02f}",
                    f"Avg Head Tilt: {metrics_data['avg_head_tilt']:.02f}",
                    f"Avg Elbow Angle: {metrics_data['avg_elbow_angle']:.02f}",
                ]
            elif phase == self.PHASE_RELEASE and metrics_data["stored"]:
                metrics_list = [
                    f"Total frame count: {metrics_data['frame_count']}",
                    f"Avg Hip Angle: {metrics_data['avg_hip_angle']:.02f}",
                    f"Avg Knee Bend: {metrics_data['avg_knee_bend']:.02f}",
                    f"Avg Elbow Angle: {metrics_data['avg_elbow_angle']:.02f}",
                    f"Max Wrist Height: {metrics_data['max_wrist_height']:.02f}",
                    f"Avg Shoulder Angle: {metrics_data['avg_shoulder_angle']:.02f}",
                    f"Avg Head Tilt: {metrics_data['avg_head_tilt']:.02f}",
                    f"Avg Body Lean: {metrics_data['avg_body_lean']:.02f}",
                    f"Avg Forearm Deviation: {metrics_data['avg_forearm_deviation']:.02f}",
                    f"Max Setpoint Distance: {metrics_data['max_setpoint']:.02f}",
                ]
            elif phase == self.PHASE_FOLLOW_THROUGH and metrics_data["stored"]:
                metrics_list = [
                    f"Total frame count: {metrics_data['frame_count']}",
                    f"Release Angle: {metrics_data['release_angle']}",
                    f"Elbow Above Eye: {metrics_data['elbow_above_eye']:.02f}",
                    f"Hip Angle: {metrics_data['hip_angle']:.02f}",
                    f"Knee Angle: {metrics_data['knee_angle']:.02f}",
                    f"Body Lean Angle: {metrics_data['body_lean_angle']:.02f}",
                    f"Head Tilt: {metrics_data['head_tilt']:.02f}",
                ]
            else:
                metrics_list = []

            for metric in metrics_list:
                cv2.putText(frame, metric, (x, y), font, 0.6, color, 2)
                y += 30