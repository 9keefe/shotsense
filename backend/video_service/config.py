OPT_SETTINGS = {
    "opt_S_avg_knee_bend": {"orig": "S_avg_knee_bend", "min": 120, "max": 160},
    "opt_S_avg_body_lean": {"orig": "S_avg_body_lean", "min": -2, "max": 4},
    "opt_S_avg_head_tilt": {"orig": "S_avg_head_tilt", "min": 50, "max": 65},
    "opt_S_avg_elbow_angle": {"orig": "S_avg_elbow_angle", "min": 45, "max": 90},
    "opt_R_avg_hip_angle": {"orig": "R_avg_hip_angle", "min": 160, "max": 185},
    "opt_R_avg_elbow_angle": {"orig": "R_avg_elbow_angle", "min": 95, "max": 145},
    "opt_R_avg_knee_bend": {"orig": "R_avg_knee_bend", "min": 154, "max": 166},
    "opt_R_max_wrist_height": {"orig": "R_max_wrist_height", "min": 3.4, "max": 7},
    "opt_R_avg_shoulder_angle": {"orig": "R_avg_shoulder_angle", "min": 15, "max": 55},
    "opt_R_avg_body_lean": {"orig": "R_avg_body_lean", "min": -3, "max": 5},
    "opt_R_forearm_deviation": {"orig": "R_avg_forearm_deviation", "min": -40, "max": 10},
    "opt_R_max_setpoint": {"orig": "R_max_setpoint", "min": -4, "max": 10},
    "opt_R_frame_count": {"orig": "R_frame_count", "min": 3, "max": 12},
    "opt_F_release": {"orig": "F_release_angle", "min": 55, "max": 79},
    "opt_F_elbow_above_eye": {"orig": "F_elbow_above_eye", "min": 7, "max": 15},
    "opt_F_hip_angle": {"orig": "F_hip_angle", "min": 174, "max": 180},
    "opt_F_knee_angle": {"orig": "F_knee_angle", "min": 170, "max": 180},
    "opt_F_body_lean": {"orig": "F_body_lean_angle", "min": -2, "max": 2.5},
    "opt_F_frame_count": {"orig": "F_frame_count", "min": 8, "max": 50},
    "opt_A_knee_bend_order": {"orig": None, "min": None, "max": None},  
    "opt_A_head_stability": {"orig": None, "min": None, "max": None}  
}

FEEDBACK_MESSAGES = {
  "opt_S_avg_knee_bend": {
    "low": {
      "short": "Too much knee bend during setup",
      "detailed": "You're bending your knees too much during the setup phase, this can disrupt your shot rhythm and lead to inconsistent power transfer and accuracy. Try to bend your knees less for a smoother shot!"
    },
    "high": {
      "short": "Not bending knees enough during setup",
      "detailed": "You're not bending your knees enough during the setup phase, this can limit power generation and reduce shot fluidity, requiring more upper-body effort. Try to activate your lower body!"
    }
  },
  "opt_S_body_lean": {
    "low": {
      "short": "Leaning too far back during setup",
      "detailed": "You're leaning too far back when loading up your shot, this can throw off your balance and reduce power transfer. Aim to lean slightly forward to maintain balance and generate a smooth shot!"
    },
    "high": {
      "short": "Leaning too far forwards during setup",
      "detailed": "Leaning too far forwards when loading up your shot can throw off your balance and power transfer, leading to inconsistencies. Try to keep your torso upright with a slight forward lean for better stability and control."
    }
  },
  "opt_S_avg_head_tilt": {
    "low": {
      "short": "Keep eyes locked to basket",
      "detailed": "Try to keep your head level and keep your eyes on the basket, maintaining body alignment. This can disrupt your balance and misalign your shooting mechanics. Try to keep your head still and eyes locked in looking at the basket at all times!"
    },
    "high": {
      "short": "Keep eyes locked to basket",
      "detailed": "Try to keep your head level and keep your eyes on the basket, maintaining body alignment. This can disrupt your balance and misalign your shooting mechanics. Try to keep your head still and eyes locked in looking at the basket at all times!"
    },
  },
  "opt_S_avg_elbow_angle": {
    "low": {
      "short": "Elbow too bent during setup",
      "detailed": "You're keeping your elbow too tight to your body, which restricts your natural shooting motion and can lead to a stiff pushing release. Try to maintain a comfortable elbow angle but keep the ball close to your body as you bring it up.",
    },
    "high": {
      "short": "Elbow not bent enough during setup",
      "detailed": "Try to keep a slight bend in your elbow as you bring the ball up to allow for a smoother ball path, ensuring a fluid, natural shooting motion."
    },
  },
  "opt_R_avg_hip_angle": {
    "low": {
      "short": "Keep body straight while bringing the ball up.",
      "detailed": "Try to keep your torso upright to maintain balance and fluidity. You're bending your hips too much, shifting your upper body forward and reducing shot arc, often leading to a flat or short shot.",
    },
    "high": {
      "short": "Error",
      "detailed": "Error"
    }
  },
  "opt_R_avg_elbow_angle": {
    "low": {
      "short": "Error",
      "detailed": "Error"
    },
    "high": {
      "short": "Keep elbow bent as you bring the ball up",
      "detailed": "Try to keep your elbow slightly bent when you bring the ball up, so you can be ready to snap and release it as you bring it up."
    }
  },
  "opt_R_avg_knee_bend": {
    "low": {
      "short": "Bend knees before bringing ball up",
      "detailed": "You're bending your knees after you brought the ball up. Try to bend your knees as you bring the ball up to your setpoint to maintain a smooth, connected shooting motion with proper rhythm and power.",
    },
    "high": {
      "short": "Straightening knees to early",
      "detailed": "You're snapping your knees too early; try to straighten your knees at the same time you straighten your elbow to create a smooth, controlled release with optimal power and better consistency."
    },
  },
  "opt_R_max_wrist_height": {
    "low": {
      "short": "Setpoint is too low",
      "detailed": "Your setpoint isn't high enough, this can lead to you 'pushing' the ball forwards instead of shooting it. Try to bring the ball higher up to improve your shot arc and to make your shot more repeatable.",
    },
    "high": {
      "short": "Error",
      "detailed": "Error"
    },
  },
  "opt_R_avg_shoulder_angle": {
    "low": {
      "short": "Arm not high enough during release",
      "detailed": "You're not moving your arm high enough during your release; try to bring your arm up and bring the ball higher to improve your shot arc and help make your shot more repeatable.",
    },
    "high": {
      "short": "Arm too high during release",
      "detailed": "You're bringing your arm too high; try to keep your setpoint lower for more consistency in your shot."
    }
  },
  "opt_R_avg_body_lean": {
    "low": {
      "short": "Leaning too far back during release",
      "detailed": "You're leaning too far back as you bring the ball up. Try to keep your body upright or lean slightly forward to avoid pushing the ball and maintain good balance.",
    },
    "high": {
      "short": "Leaning too far forward during release",
      "detailed": "You're leaning too far forward as you bring the ball up. While a slight forward lean is good, too much can disrupt your balance. Try to lean back a bit to keep your center of gravity centered."
    }, 
  },
  "opt_R_forearm_deviation": {
    "low": {
      "short": "Hand not underneath ball",
      "detailed": "Try to get your forearm directly underneath the ball and bring it up in a straight path to generate enough power for a good shot arc.",
    },
    "high": {
      "short": "Hand not underneath ball",
      "detailed": "You're 'pushing' the ball rather than bringing it up; try to get your forearm directly underneath the ball and bring it up in a straight path to generate sufficient power."
    }
  },
  "opt_R_max_setpoint": {
    "low": {
      "short": "Setpoint too far back",
      "detailed": "Your setpoint is too far back behind your head. This negatively affects your shot control, power efficiency, and accuracy. Try to keep your setpoint in front of your forehead or slightly above eye level.",
    },
    "high": {
      "short": "Setpoint too far forward",
      "detailed": "Your setpoint is too far forward. This can lead to an inconsistent shot form and a weak release. Try to keep your setpoint in front of your forehead or slightly above eye level."
    },
  },
  "opt_R_frame_count": {
    "low": {
      "short": "Not bringing ball to setpoint",
      "detailed":"You're releasing the ball without bringing it to your setpoint first. This can disrupt your control and power transfer, leading you to 'push' your shot. Try to bring the ball up to your setpoint before releasing.",
    },
    "high": {
      "short": "Pausing during setpoint",
      "detailed": "You're slightly pausing when you reach your setpoint, which can disrupt your shooting fluidity and release consistency. Try to shoot in one motion as you bring the ball up and release it."
    } 
  },
  "opt_F_release": {
    "low": {
      "short": "Release angle too low",
      "detailed": "Your release angle is too low. Try to aim for an elbow level around your eyebrow at release for a good arc.",
    },
    "high": {
      "short": "Release angle too high",
      "detailed": "Your release angle is too high. While a higher arc can be beneficial, too high an arc makes depth control difficult, leading to inconsistency. Aim for a high but controlled arc with your elbow around your eyebrow."
    }
  },
  "opt_F_hip_angle": {
    "low": {
      "short": "Body not straight as you shoot",
      "detailed": "Your body isn't straight during release, causing power to be generated only by your arms. Straighten your body and hips for a more balanced, coordinated shot.",
    },
    "high": {
      "short": "Error",
      "detailed": "Error"
    },
  },
  "opt_F_knee_angle": {
    "low": {
      "short": "Knees not straight as you shoot",
      "detailed": "Your body isn't straight during release, causing power to be generated only by your arms. Straighten your body and legs to allow your whole body to contribute.",
    },
    "high": {
      "short": "Error",
      "detailed": "Error"
    },
  },
  "opt_F_body_lean": {
    "low": {
      "short": "Leaning too far back as you shoot",
      "detailed": "You're leaning too far back as you shoot, which can cause inconsistencies. Try to keep your body straight during release.",
    },
    "high": {
      "short": "Leaning too far forward as you shoot",
      "detailed": "You're leaning too far forward as you shoot, which can disrupt your balance. Aim to keep your body straight during release."
    }
  },
  "opt_F_frame_count": {
    "low": {
      "short": "Not holding follow-through",
      "detailed": "Try to hold your follow-through consistently to self-assess your release and reinforce good mechanics.",
    },
    "high": {
      "short": "Error",
      "detailed": "Error"
    },
  },
  "opt_A_knee_bend_order": {
    "special": {
      "short": "Knees bending after moving ball up",
      "detailed": "Try to bend your knees before moving the ball up, rather than after, to improve fluidity and ensure smoother energy transfer."
    }
  },
  "opt_A_head_stability": {
    "special": {
      "short": "Head not still during shot",
      "detailed": "Try to focus on the rim and keep your head still throughout your shot preparation and execution to maintain head stability."
    }
  }
}


FEEDBACK_COLS = [
  "opt_S_avg_knee_bend", 
  "opt_S_avg_elbow_angle",
  "opt_R_avg_shoulder_angle",
  "opt_R_max_wrist_height",
  "opt_R_avg_body_lean",
  "opt_R_max_setpoint",
  "opt_R_forearm_deviation",
  "opt_R_avg_elbow_angle",
  "opt_R_frame_count",
  "opt_F_release",
  "opt_F_hip_angle",
  "opt_F_knee_angle",
  "opt_F_body_lean",
  "opt_F_frame_count",
  "opt_A_knee_bend_order",
  "opt_A_head_stability"
]