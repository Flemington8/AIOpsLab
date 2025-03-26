import json
import os
import glob
from aiopslab.paths import RESULTS_DIR

def parse_value(val):
    """Convert 'Correct'/'Incorrect' to 1.0/0.0 or parse float if possible."""
    if isinstance(val, (float, int, bool)):
        return float(val)
    if val == "Correct":
        return 1.0
    if val == "Incorrect":
        return 0.0
    try:
        return float(val)
    except:
        return None

def analyze_results(directory):
    # Keep only one entry per (agent, problem_id)
    processed = {}

    # Collect per-task metrics
    detection_data = []
    mitigation_data = []
    localization_data = []
    root_cause_analysis_data = []

    for file_path in glob.glob(os.path.join(directory, "*.json")):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except:
                continue
            # Filter agent
            if data.get("agent") != "deepseek-r1":
                continue
            problem_id = data.get("problem_id")
            if not problem_id:
                continue
            # Skip if we've already stored this problem_id
            if problem_id in processed:
                continue
            processed[problem_id] = True

            results = data.get("results", {})
            # Detection
            if "detection" in problem_id:
                acc = parse_value(results["Detection Accuracy"])
                ttd = parse_value(results.get("TTD", None))
                steps = parse_value(results.get("steps", None))
                if acc is not None and ttd is not None and steps is not None:
                    detection_data.append((acc, ttd, steps))
            # Localization
            if "localization" in problem_id:
                lacc = parse_value(results["Localization Accuracy"])
                ttl = parse_value(results.get("TTL", None))
                steps = parse_value(results.get("steps", None))
                if lacc is not None and ttl is not None and steps is not None:
                    localization_data.append((lacc, ttl, steps))
            # Root cause analysis
            if "analysis" in problem_id:
                slc = 1.0 if results.get("system_level_correct") else 0.0
                ftc = 1.0 if results.get("fault_type_correct") else 0.0
                success = parse_value(results["success"])
                ttr = parse_value(results.get("TTR", None))
                steps = parse_value(results.get("steps", None))
                if slc is not None and ftc is not None and success is not None and ttr is not None and steps is not None:
                    root_cause_analysis_data.append((slc, ftc, success, ttr, steps))
            # Mitigation
            if "mitigation" in problem_id:
                success = parse_value(results["success"])
                ttm = parse_value(results.get("TTM", None))
                steps = parse_value(results.get("steps", None))
                if success is not None and ttm is not None and steps is not None:
                    mitigation_data.append((success, ttm, steps))

    # Compute averages
    def avg(lst, idx):
        return sum(item[idx] for item in lst) / len(lst) if lst else 0.0

    # Detection
    print("Detection tasks:")
    if detection_data:
        print("  Number of problems:", len(detection_data))
        print("  Average Detection Accuracy(%):", avg(detection_data, 0) * 100)
        print("  Average TTD:", avg(detection_data, 1))
        print("  Average steps:", avg(detection_data, 2))
    else:
        print("  No data")

    # Localization
    print("Localization tasks:")
    if localization_data:
        print("  Number of problems:", len(localization_data))
        print("  Average Localization Accuracy(%):", avg(localization_data, 0))
        print("  Average TTL:", avg(localization_data, 1))
        print("  Average steps:", avg(localization_data, 2))
    else:
        print("  No data")

    # Root cause analysis
    print("Root cause analysis tasks:")
    if root_cause_analysis_data:
        print("  Number of problems:", len(root_cause_analysis_data))
        print("  Average System-Level Correct(%):", avg(root_cause_analysis_data, 0) * 100)
        print("  Average Fault-Type Correct(%):", avg(root_cause_analysis_data, 1) * 100)
        print("  Average Root Cause Analysis Success(%):", avg(root_cause_analysis_data, 2) * 100)
        print("  Average TTR:", avg(root_cause_analysis_data, 3))
        print("  Average steps:", avg(root_cause_analysis_data, 4))
    else:
        print("  No data")

    # Mitigation
    print("Mitigation tasks:")
    if mitigation_data:
        print("  Number of problems:", len(mitigation_data))
        print("  Average Mitigation Success(%):", avg(mitigation_data, 0) * 100)
        print("  Average TTM:", avg(mitigation_data, 1))
        print("  Average steps:", avg(mitigation_data, 2))
    else:
        print("  No data")

if __name__ == "__main__":
    analyze_results(RESULTS_DIR)