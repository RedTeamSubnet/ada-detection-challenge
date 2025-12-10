---
title: Zero-FP Browser Integrity (ZFBI) Challenge Submission Guide
---
# Zero-FP Browser Integrity (ZFBI) Challenge Submission Guide

## Overview

The **Zero-FP Browser Integrity (ZFBI) Challenge** focuses on detecting how various automation frameworks utilize web sockets and other stealth techniques to control browsers. This challenge requires participants to develop precise detection scripts capable of identifying specific automation tools (while they operate within the **NST-Browser** environment) and, crucially, to distinguish them from genuine human interaction.

Participants must demonstrate robust detection capabilities across multiple target frameworks, ensuring reliability in different execution modes. A critical aspect of the challenge is maintaining a zero-false-positive rate when a human user interacts with the browser.

---

## Technical Requirements

* **SDK Development**: Your solution will consist of JavaScript detection files.
* **Execution Environment**: Your detection scripts will be executed within a browser controlled by **NST-Browser**.
* **Submission Format**: Your scripts are submitted as raw JavaScript content via an API call (not as a bundled SDK or Docker image).
* **Development Environment**: Participants are encouraged to develop and test their solutions in a separate GitHub repository, then submit the raw detection scripts.

### Mandatory Requirements

1. **File Structure**: You must provide a separate JavaScript file (`.js`) for each target automation framework.
2. **Detection Logic**: Implement your detection logic within these individual files.
3. **Function Naming**: The file name (e.g., `nodriver.js`) should correspond to the specific framework it aims to detect.
4. **Output Format**: Your detection function(s) within each file should ultimately report whether the specific framework for that file was detected. This is communicated back to the challenge server via the `/_payload` endpoint.
5. **Human Detection**: Your submitted scripts are expected to remain silent (i.e., not detect any automation) during genuine human interaction. If any of your scripts report a detection during a human session, it will be considered a false positive.

### Target Automation Frameworks

Your detection scripts should be capable of accurately identifying the following automation frameworks when they interact with the NST-Browser:

* **nodriver**
* **playwright**
* **patchright**
* **puppeteer**

---

## Key Guidelines

* **Detection Method**: Focus on analyzing automation behavior, unique signatures, or behavioral patterns within the browser environment.
* **Execution Modes**: Your scripts will be tested in environments that simulate various browser execution modes.
* **Reliability**: The reliability of your scripts will be assessed across multiple test sessions for each target.
* **Limitations**
  * Your script must not exceed **500 lines** of JavaScript code. Submissions exceeding this limit will receive a score of zero.
  * **Prohibited Methods**: Solutions relying on traditional browser fingerprinting techniques are strictly forbidden. Any such solution detected will result in immediate disqualification and a score of zero.

---

## Evaluation Criteria

The challenge evaluates:

* **Detection Accuracy**: Correctly identifying automation frameworks by name.
* **Consistency**: Maintaining accuracy across multiple test runs for each framework.
* **Human Classification**: The ability to correctly classify genuine human interaction as non-automated.
* **False Positive Avoidance**: Minimizing false positives, especially for human interaction.

### Scoring System

The final score is calculated based on performance across multiple evaluation sessions for each target (automation frameworks and human interaction).

* **Human as Bot = 0 Score**: If your script incorrectly identifies the human user as a bot more than the allowed number of times, your **final score for the entire submission is 0**, regardless of how well you detected the actual bots.
* **Perfect Human Detection**: Correctly classifying the human in all runs (meaning your scripts report no detections during human interaction) earns you **1 full point** towards your total.
* **Perfect Bot Detection**: Correctly identifying a specific bot framework across all its test runs (e.g., 3 out of 3 times) without any collisions earns **1 full point** per framework.
* **Collisions**: If you correctly identify a bot but *also* identify other frameworks incorrectly at the same time (a "collision"), you receive a reduced score of **0.1 points** for that run.
* **Final Score Calculation**: The final score is a normalized calculation: `Final Score = (Total Points Earned) / (Number of Target Frameworks + 1)` (where "+1" accounts for the human interaction test).

### Plagiarism Check

We maintain strict originality standards:

* All submissions are compared against other participants' submissions.
* 100% similarity will result in a zero score.
* Similarity above 60% will result in proportional score penalties based on the detected similarity percentage.

### Pre-Submission Check

Before submitting, ensure your code adheres to required linting standards. You may be provided with tools or environments to verify this.

---

## Submission Guide

To submit your detection scripts for evaluation, you will send an authenticated `POST` request to the challenge server's `/score` API endpoint.

**1. Authentication:**

* You will need an API key for authentication, which is typically provided as a `REWARDING_SECRET_KEY` in your environment.

**2. Request Body:**

* The request body must be a JSON object containing a list of your detection scripts. Each script is represented as an object with its `file_name` and the `content` (raw JavaScript code) of the script.

**Example Request Body (JSON):**

```json
{
  "detection_files": [
    {
      "file_name": "nodriver.js",
      "content": "/* Your JavaScript code to detect nodriver */"
    },
    {
      "file_name": "playwright.js",
      "content": "/* Your JavaScript code to detect playwright */"
    },
    // ... include all other target framework scripts ...
    {
      "file_name": "zendriver.js",
      "content": "/* Your JavaScript code to detect zendriver */"
    }
  ]
}
```

*(Note: You must provide one JavaScript file for every target automation framework listed in the "Target Automation Frameworks" section above.)*

---

## 📑 References

* Docker - <https://docs.docker.com>
* NST-Browser - (Relevant documentation link for NST-Browser would go here)
