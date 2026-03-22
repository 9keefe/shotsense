import os

import joblib
import numpy as np
import pandas as pd

from .config import FEEDBACK_COLS, FEEDBACK_MESSAGES, OPT_SETTINGS


MODEL_FOLDER = os.path.join(os.path.dirname(__file__), "model")

MODEL_FORM = joblib.load(os.path.join(MODEL_FOLDER, "model_form_6_scale.pkl"))
OPT_COLS = joblib.load(os.path.join(MODEL_FOLDER, "opt_cols_v3.pkl"))
ALL_OPT_COLS = joblib.load(os.path.join(MODEL_FOLDER, "all_opt_cols.pkl"))


def get_model_feedback(features):
  try:
    df_orig = pd.DataFrame([features])

    all_opt_df = generate_opt_table(df_orig)
    model_opt_df = all_opt_df[OPT_COLS]

    form_probs = MODEL_FORM.predict_proba(model_opt_df)
    final_score = calculate_percentage(form_probs, 5)

    feedback_df = all_opt_df[FEEDBACK_COLS]
    top_feedback = get_top_feedback(feedback_df, df_orig, 5)

    return final_score, top_feedback

  except Exception as e:
    print(f"Model inference error: {str(e)}")
    return None, None


def get_top_feedback(opt_df, df_orig, top_n=10):
  scores = opt_df.iloc[0].to_dict()
  non_optimal = {col: score for col, score in scores.items() if score != 100}

  sorted_features = sorted(non_optimal.items(), key=lambda x: x[1])
  top_features = sorted_features[:top_n]

  feedback_list = []
  for feature, score_value in top_features:
    settings = OPT_SETTINGS.get(feature, {})
    raw_val = None
    direction = "optimal"

    if settings.get("orig"):
      raw_val = df_orig.iloc[0].get(settings["orig"])
      if raw_val < settings["min"]:
        direction = "low"
      else:
        direction = "high"
    else:
      direction = "special"

    optimal_range_str = ""
    if settings.get("min") is not None and settings.get("max") is not None:
      optimal_range_str = f"\nOptimal range: Between {round(settings['min'], 1)} and {round(settings['max'], 1)}"

    short_msg = ""
    detailed_msg = ""

    if feature in FEEDBACK_MESSAGES:
      feedback_for_feature = FEEDBACK_MESSAGES[feature]
      if direction in feedback_for_feature:
        feedback_item = feedback_for_feature[direction]
        if isinstance(feedback_item, dict):
          short_msg = feedback_item.get("short", "")
          detailed_msg = feedback_item.get("detailed", "")
        else:
          short_msg = feedback_item
          detailed_msg = feedback_item
      else:
        short_msg = "ERROR"
        detailed_msg = "ERROR"
    else:
      short_msg = "ERROR"
      detailed_msg = "ERROR"

    if raw_val is not None:
      feature_name = parse_metric(settings.get("orig", feature))[2:]
      detailed_msg += f"\n\n{feature_name}\nCurrent value: {round(raw_val, 1)} {optimal_range_str}"

    feedback_list.append({
      "feature": feature,
      "score": score_value,
      "direction": direction,
      "short": short_msg,
      "detailed": detailed_msg,
    })

  return feedback_list


def score(val, opt_min, opt_max):
  if val < opt_min:
    return -((opt_min - val) ** 2)
  if val > opt_max:
    return -((val - opt_max) ** 2)
  return 100


def generate_opt_table(df):
  df = df.copy()
  df["opt_S_avg_knee_bend"] = df["S_avg_knee_bend"].apply(lambda x: score(x, 120, 160))
  df["opt_S_avg_body_lean"] = df["S_avg_body_lean"].apply(lambda x: score(x, -2, 4))
  df["opt_S_avg_head_tilt"] = df["S_avg_head_tilt"].apply(lambda x: score(x, 50, 65))
  df["opt_S_avg_elbow_angle"] = df["S_avg_elbow_angle"].apply(lambda x: score(x, 45, 90))

  df["opt_R_avg_hip_angle"] = df["R_avg_hip_angle"].apply(lambda x: score(x, 160, 180))
  df["opt_R_avg_elbow_angle"] = df["R_avg_elbow_angle"].apply(lambda x: score(x, 95, 145))
  df["opt_R_avg_knee_bend"] = df["R_avg_knee_bend"].apply(lambda x: score(x, 154, 166))
  df["opt_R_max_wrist_height"] = df["R_max_wrist_height"].apply(lambda x: score(x, 3.4, 7))
  df["opt_R_avg_shoulder_angle"] = df["R_avg_shoulder_angle"].apply(lambda x: score(x, 15, 55))
  df["opt_R_avg_body_lean"] = df["R_avg_body_lean"].apply(lambda x: score(x, -3, 5))
  df["opt_R_forearm_deviation"] = df["R_avg_forearm_deviation"].apply(lambda x: score(x, -40, 10))
  df["opt_R_max_setpoint"] = df["R_max_setpoint"].apply(lambda x: score(x, -4, 10))
  df["opt_R_frame_count"] = df["R_frame_count"].apply(lambda x: score(x, 3, 12))

  df["opt_F_release"] = df["F_release_angle"].apply(lambda x: score(x, 55, 79))
  df["opt_F_elbow_above_eye"] = df["F_elbow_above_eye"].apply(lambda x: score(x, 7, 15))
  df["opt_F_hip_angle"] = df["F_hip_angle"].apply(lambda x: score(x, 174, 180))
  df["opt_F_knee_angle"] = df["F_knee_angle"].apply(lambda x: score(x, 170, 180))
  df["opt_F_body_lean"] = df["F_body_lean_angle"].apply(lambda x: score(x, -2, 2.5))
  df["opt_F_frame_count"] = df["F_frame_count"].apply(lambda x: score(x, 8, 50))

  df["opt_A_knee_bend_order"] = df.apply(
    lambda row: 100 if row["S_avg_knee_bend"] < row["R_avg_knee_bend"] + 3 else -100,
    axis=1,
  )

  df["opt_A_head_stability"] = df.apply(score_head_tilt, axis=1)

  return df[ALL_OPT_COLS].copy()


def score_head_tilt(row, threshold=15):
  head_tilts = [row["S_avg_head_tilt"], row["R_avg_head_tilt"], row["F_head_tilt"]]
  std_dev = np.std(head_tilts)
  return 100 if std_dev <= threshold else -100


def calculate_percentage(probabilities, max_class):
  label_scores = np.array([i / max_class * 100 for i in range(max_class + 1)])
  final_score = np.sum(probabilities * label_scores)
  return final_score + 10


def parse_metric(metric):
  parts = metric.split("_")
  new_parts = []

  for part in parts:
    if part.lower() == "avg":
      new_parts.append("Average")
    else:
      new_parts.append(part.capitalize())

  return " ".join(new_parts)


def parse_all_metrics(metrics_dict):
  parsed = {}
  for key, value in metrics_dict.items():
    parsed_key = parse_metric(key)
    parsed[parsed_key] = value
  return parsed