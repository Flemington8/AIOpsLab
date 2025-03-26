import json
import os
import re


def parse_output_log(log_path, results_dir):
    """
    Reads the output.log file and extracts:
      - problem_id, session_id
      - whether there's an invalid solution format
      - any error message (e.g., timeout)
      - matching JSON data (agent, session_id, etc.) if found in results_dir
    Returns a list of dict with the final report entries.
    """

    re_success = re.compile(r"Successfully processed pid\s+(.*)\.")
    re_failed = re.compile(r"Failed to process pid\s+(.*)\.\s+Error:\s+(.*)")
    re_session = re.compile(r"Session ID:\s+([a-f0-9\-]+)")
    re_eval_block = re.compile(r"== Evaluation ==")
    re_invalid_solution = re.compile(r"Invalid solution format")

    report_entries = []
    current_session_id = None
    current_problem_id = None
    current_session_invalid_format = False

    if not os.path.isfile(log_path):
        return report_entries

    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # Check for a session ID
        match_session = re_session.search(line)
        if match_session:
            current_session_id = match_session.group(1)

        # Detect an "== Evaluation ==" block to see if there's invalid format
        if re_eval_block.search(line):
            # Look ahead to see if there's "Invalid solution format" or an "Invalid Format" result
            look_ahead = i + 1
            while look_ahead < len(lines):
                if lines[look_ahead].startswith("== "):
                    break
                if re_invalid_solution.search(lines[look_ahead]):
                    current_session_invalid_format = True
                look_ahead += 1

        # If we see a success message, finalize the current session
        match_success = re_success.search(line)
        if match_success:
            current_problem_id = match_success.group(1)
            if current_session_id:
                report_entries.append({
                    "session_id": current_session_id,
                    "problem_id": current_problem_id,
                    "agent": None,
                    "results": None,
                    "invalid_format": current_session_invalid_format,
                    "error": None
                })
            # Reset for the next session
            current_session_id = None
            current_problem_id = None
            current_session_invalid_format = False

        # Check for a failure message—finalize the session similarly
        match_fail = re_failed.search(line)
        if match_fail:
            current_problem_id = match_fail.group(1)
            fail_msg = match_fail.group(2)
            if current_session_id:
                report_entries.append({
                    "session_id": current_session_id,
                    "problem_id": current_problem_id,
                    "agent": None,
                    "results": None,
                    "invalid_format": current_session_invalid_format,
                    "error": fail_msg
                })
            # Reset after fail
            current_session_id = None
            current_problem_id = None
            current_session_invalid_format = False

        i += 1

    # Attempt to match each session ID with a corresponding JSON file in results_dir
    session_json_map = {}
    if os.path.isdir(results_dir):
        for f_name in os.listdir(results_dir):
            # e.g. c20fba6b-8c92-4d93-8898-f1827d6ec4ac_stuff.json
            parts = f_name.split("_", 1)
            if len(parts) == 2:
                sid_prefix = parts[0]
                session_json_map[sid_prefix] = f_name

    for entry in report_entries:
        sid = entry["session_id"]
        if not sid:
            continue
        if sid in session_json_map:
            json_path = os.path.join(results_dir, session_json_map[sid])
            if os.path.isfile(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as jfile:
                        data = json.load(jfile)
                        entry["agent"] = data.get("agent", None)
                        entry["results"] = data.get("results", None)
                except Exception as e:
                    entry["json_error"] = f"Failed to read JSON: {e}"
        else:
            # If we can't find a corresponding JSON
            entry["json_error"] = "No matching JSON"

    return report_entries


def parse_all_runs(wandb_dir, results_dir):
    """
    Finds all directories under wandb_dir named 'run-*' and parses each 'output.log'
    inside the 'files' subdirectory, then aggregates all results.
    """
    all_reports = []
    if not os.path.isdir(wandb_dir):
        return all_reports

    for run_dir in os.listdir(wandb_dir):
        if run_dir.startswith("run-"):
            files_subdir = os.path.join(wandb_dir, run_dir, "files")
            if os.path.isdir(files_subdir):
                log_path = os.path.join(files_subdir, "output.log")
                reports = parse_output_log(log_path, results_dir)
                all_reports.extend(reports)

    return all_reports


if __name__ == "__main__":
    # Example usage:
    wandb_dir = "./wandb"
    results_dir = "./aiopslab/data/results"

    final_report = parse_all_runs(wandb_dir, results_dir)
    # Save the final report to a file
    output_path = os.path.join(wandb_dir, "final_report.json")
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(final_report, outfile, indent=2)
    print(f"Final report saved to {output_path}")
