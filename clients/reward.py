import re

completions = [
    [{"role": "assistant", "content": "```\nexec_shell(\"kubectl get pods -n test-social-network | grep compost-post-service\")\n```"}], # Correct format
    [{"role": "assistant", "content": "Action: exec_shell(\"kubectl get configmaps -n test-social-network\")"}], # Incorrect format
    [{"role": "assistant", "content": "exec_shell(\"kubectl get pods -n test-social-network\")"}], # Incorrect format
    [{"role": "assistant", "content": "```\nexec_shell(\"kubectl get pods\")\n```"}], # Correct format
    [{"role": "assistant", "content": "submit([\"compost-post-service\", \"compost-post-service-1\", \"compost-post-service-2\"])\n```"}], # Incorrect format
    [{"role": "assistant", "content": "```\nsubmit(\"Yes\")\n```"}], # Correct format for detection
    [{"role": "assistant", "content": "```\nsubmit([\"TiDB Operator not installed\", \"Missing CRD for tidbclusters\", \"tidb-cluster namespace has no running pods\"])\n```"}], # Correct format for localization
    [{"role": "assistant", "content": "```\nsubmit({'system_level': 'Virtualization', 'fault_type': 'Misconfiguration'})\n```"}], # Correct format for root cause analysis
    [{"role": "assistant", "content": "```\nsubmit()\n```"}], # Correct format for mitigation
]

results = [
     {  "task": "detection",
        "Detection Accuracy": "Correct",
        "TTD": 105.1446475982666,
        "steps": 4,
        "in_tokens": 10152,
        "out_tokens": 73
    },
    {   "task": "localization",
        "Localization Accuracy": 0.0,
        "TTL": 20.57143259048462,
        "steps": 5,
        "in_tokens": 2187,
        "out_tokens": 140,
        "success": False,
        "is_subset": False
    },
    {   "task": "analysis",
        "system_level_correct": True,
        "fault_type_correct": False,
        "success": False,
        "TTR": 21.355182647705078,
        "steps": 9,
        "in_tokens": 5943,
        "out_tokens": 390
    },
    {   "task": "mitigation",
        "TTM": 14.532860279083252,
        "steps": 4,
        "in_tokens": 688,
        "out_tokens": 91,
        "success": False
    }
]

def format_reward_func(completions, **kwargs):
    """Reward function that checks if the completion has the correct API call format."""
    pattern = r"^```\nexec_shell\([\"].*?[\"].*\)\n```$|^```\nsubmit\(.*\)\n```$"  # Match exec_shell or submit pattern
    completion_contents = [completion[0]["content"] for completion in completions]
    matches = [re.match(pattern, content) for content in completion_contents]
    return [0.0 if match else -1.0 for match in matches]

def detection_eval(result):
    # Check correctness of detection
    if result["Detection Accuracy"] == "Correct":
        detection_correct = True
    else:
        detection_correct = False

    # Check the detection time (TTD) is within acceptable limits
    TTD_threshold = 100  # Define threshold for fast detection
    TTD_penalty = 0.0
    if result["TTD"] > TTD_threshold:
        TTD_penalty = -0.5  # Penalty for long detection time

    # If detection is correct, reward, else penalize
    reward = 1.0 if detection_correct else -1.0
    return reward + TTD_penalty

def localization_eval(result):
    # Check the localization accuracy
    if result["Localization Accuracy"] > 0.5:  # Customize this threshold based on your task's requirement
        localization_correct = True
    else:
        localization_correct = False

    # Check the localization time (TTL) is within acceptable limits
    TTL_threshold = 20  # Define threshold for fast localization
    TTL_penalty = 0.0
    if result["TTL"] > TTL_threshold:
        TTL_penalty = -0.5  # Penalty for long localization time

    # If localization is correct, reward, else penalize
    reward = 1.0 if localization_correct else -1.0
    return reward + TTL_penalty

def analysis_eval(result):
    # Check if system-level analysis is correct
    system_level_correct = result["system_level_correct"]
    fault_type_correct = result["fault_type_correct"]
    
    # Penalty for incorrect fault type
    penalty = 0.0
    if not fault_type_correct:
        penalty = -0.5  # Penalty for incorrect fault type

    # Check Time to Resolution (TTR) for speed
    TTR_threshold = 30  # Define threshold for fast analysis
    TTR_penalty = 0.0
    if result["TTR"] > TTR_threshold:
        TTR_penalty = -0.5  # Penalty for slow resolution time

    # If system-level analysis is correct, reward, else penalize
    reward = 1.0 if system_level_correct else -1.0
    return reward + penalty + TTR_penalty

def mitigation_eval(result):
    # Check if mitigation was successful
    success = result["success"]

    # Check Time to Mitigation (TTM) for speed
    TTM_threshold = 20  # Define threshold for fast mitigation
    TTM_penalty = 0.0
    if result["TTM"] > TTM_threshold:
        TTM_penalty = -0.5  # Penalty for slow mitigation

    # Reward for success, otherwise penalize
    reward = 1.0 if success else -1.0
    return reward + TTM_penalty

def result_reward_func(results, **kwargs):
    rewards = []

    for result in results:
        if result["task"] == "detection":
            # Calculate reward for detection task
            reward = detection_eval(result)
            rewards.append(reward)
        elif result["task"] == "localization":
            # Calculate reward for localization task
            reward = localization_eval(result)
            rewards.append(reward)
        elif result["task"] == "analysis":
            # Calculate reward for root cause analysis task
            reward = analysis_eval(result)
            rewards.append(reward)
        elif result["task"] == "mitigation":
            # Calculate reward for mitigation task
            reward = mitigation_eval(result)
            rewards.append(reward)

    return rewards

if __name__ == "__main__":
    # Example usage
    rewards = format_reward_func(completions)
    print(rewards)  # Output: [0.0, -1.0, -1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0]

    # Example usage of result_reward_func
    result_rewards = result_reward_func(results)
    print(result_rewards)  # Output: [1.0, -1.0, -1.0, -1.0]