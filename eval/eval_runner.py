import json
import sys
import os
import time
sys.path.insert(0, os.getcwd())
from app.classifier import classify_message
from app.schemas import MessageInput

def classify_with_retry(msg_id, text, max_retries=5):
    for attempt in range(max_retries):
        try:
            return classify_message(MessageInput(id=msg_id, text=text))
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "quota" in err.lower() or "unavailable" in err.lower():
                wait = 60 if "429" in err else 30
                print(f"API error on attempt {attempt+1}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise Exception(f"Failed after {max_retries} retries")

def run_eval(gold_set_path="eval/gold_set.jsonl"):
    with open(gold_set_path, "r") as f:
        messages = [json.loads(line) for line in f]
    correct = 0
    safety_correct = 0
    safety_total = 0
    safety_classes = ["red_flag_escalation", "urgent_clinical_review"]
    print("Running evaluation...")
    for i, msg in enumerate(messages):
        if i > 0 and i % 4 == 0:
            print("Pausing 60s to respect rate limit...")
            time.sleep(60)
        result = classify_with_retry(msg["id"], msg["text"])
        expected = msg["label"]
        predicted = result.primary_label.value
        match = predicted == expected
        if match:
            correct += 1
        if expected in safety_classes:
            safety_total += 1
            if match:
                safety_correct += 1
        status = "PASS" if match else "FAIL"
        msg_id = msg["id"]
        print(f"[{status}] {msg_id} | Expected: {expected} | Got: {predicted}")
    total = len(messages)
    accuracy = correct / total
    safety_recall = safety_correct / safety_total if safety_total > 0 else 1.0
    print("")
    print("--- Evaluation Results ---")
    print(f"Total: {total} | Correct: {correct} | Accuracy: {accuracy:.2%}")
    print(f"Safety recall: {safety_recall:.2%} ({safety_correct}/{safety_total})")
    if safety_recall >= 0.95:
        print("Safety recall target met.")
    else:
        print("WARNING: Safety recall below 95% target.")

if __name__ == "__main__":
    run_eval()
