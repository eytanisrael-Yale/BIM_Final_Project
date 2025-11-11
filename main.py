#!/usr/bin/env python3
# pip install google-generativeai

import os
import sys
import datetime
import google.generativeai as genai

MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

MASTER_PROMPT = r"""
You will see ONE IMAGE.

Context:
You are helping a social robot address a specific person within a group by saying a single, brief line that starts with “Hey you, …” so the person instantly knows it’s them, 
and no other person is confused.

Task:
1) Produce THREE independent, single-sentence call-outs (D1–D3) the robot could say:
   - D1: concise, natural “Hey you, …” that uniquely identifies the bounded person.
   - D2: “Hey you, …” that highlights distinctive clothing/accessories AND a relative location (e.g., “front-left”).
   - D3: the briefest possible “Hey you, …” that still uniquely identifies the bounded person.

Rules for D1–D3:
- Each description MUST begin with exactly: "Hey you, ".
- Treat D1–D3 independently. Do NOT let one influence the others.
- Use only what’s visible in the image. No speculation (no age/identity/ethnicity).
- Be maximally discriminative and succinct: concrete clothing colors/patterns, salient accessories, relative position cues.
- Avoid extra words or narrative; write each as a direct call-out the robot will speak.

2) Judge and rank D1–D3 (1=best, 3=worst) with ratings 0–10.
Evaluation goal: Would an average bystander clearly identify the bounded person from this single line, and is it as brief as possible?
Tie-breakers: (a) discriminative power, (b) brevity, (c) clarity.

Return ONLY valid compact JSON exactly in this schema:
{
  "descriptions": [
    {"idx": 1, "text": "<D1>"},
    {"idx": 2, "text": "<D2>"},
    {"idx": 3, "text": "<D3>"}
  ],
  "items": [
    {"idx": 1, "rating": <int 0-10>, "rank": <1|2|3>, "justification": "<short reason>", "issues": ["<bullet>", "..."]},
    {"idx": 2, "rating": <int 0-10>, "rank": <1|2|3>, "justification": "<short reason>", "issues": ["<bullet>", "..."]},
    {"idx": 3, "rating": <int 0-10>, "rank": <1|2|3>, "justification": "<short reason>", "issues": ["<bullet>", "..."]}
  ],
  "overall_notes": "<one- or two-sentence comparison across all three>"
}
"""

def main(image_path: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: set GEMINI_API_KEY in your environment.")
        sys.exit(1)
    genai.configure(api_key=api_key)

    try:
        file_ref = genai.upload_file(image_path)
    except Exception as e:
        print(f"Error uploading image: {e}")
        sys.exit(1)

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=(
            "Work ONLY from the provided image. Do not use outside context or prior turns. "
            "All outputs must adhere to the JSON schema and each description should start with 'Hey you, '."
        ),
        generation_config={"response_mime_type": "application/json"}
    )

    try:
        resp = model.generate_content([file_ref, {"text": MASTER_PROMPT}])
        raw_output = (getattr(resp, "text", None) or "").strip()
    except Exception as e:
        print(f"Model error: {e}")
        sys.exit(1)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = os.path.splitext(os.path.basename(image_path))[0]
    out_file = f"{img_name}_{timestamp}.txt"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"Image: {image_path}\n\n=== MODEL OUTPUT ===\n{raw_output}\n")

    print(f"Results saved to {out_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <image_path>")
        sys.exit(1)
    main(sys.argv[1])
