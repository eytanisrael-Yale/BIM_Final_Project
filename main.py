#!/usr/bin/env python3
# pip install google-generativeai

import os
import sys
import datetime
import google.generativeai as genai


MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _mime(path: str) -> str:
    ext = path.lower()
    if ext.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if ext.endswith(".webp"):
        return "image/webp"
    return "image/png"


def gemini_text_from_image(prompt: str, image_path: str) -> str:
    """Send an image and prompt to Gemini and return the text response."""
    model = genai.GenerativeModel(MODEL)
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    resp = model.generate_content(
        [{"mime_type": _mime(image_path), "data": img_bytes}, prompt]
    )
    return (getattr(resp, "text", None) or "").strip()


def run(image_path: str):
    """Generate three descriptions and one comparative judgment."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: set GEMINI_API_KEY in your environment.")
        sys.exit(1)
    genai.configure(api_key=api_key)

    # Prompts for description generation
    prompts = [
        "Describe, in one concise sentence, the bounded individual. ",
        "In one sentence, specify the bounded person’s distinctive clothing/accessories and relative location (e.g., front-left, near X) so a bystander can pick them out instantly. ",
        "Describe the bounded person as briefly as possible, while still identifying only them in the picture. ",
    ]
    context = (
        "Make the sentence such that you could say 'Hey you, ...' and they'd know it's them. "
        "Make the description as brief as possible without any descriptors that aren't necessary. "
    )

    # Generate 3 descriptions
    descriptions = [gemini_text_from_image(p + context, image_path) for p in prompts]

    # Single comparative judge call (model ranks all three together)
    judge_prompt = f"""
You are a harsh evaluator. Given the IMAGE and THREE DESCRIPTIONS, evaluate and rank them
relatively (1=best, 3=worst). Break ties by (a) discriminative power, (b) brevity, then (c) clarity.

Goal: Would an average bystander clearly identify the bounded individual from this *single* sentence?
Is it as brief as possible with no extra words?

Scoring (0–10 for each description):
- 9–10: Unambiguous, concrete, highly specific (distinctive clothing, relative position, salient accessories), no speculation, no extra words.
- 6–8: Mostly clear but with some vagueness or unnecessary language.
- 3–5: Vague or generic; could match multiple people.
- 0–2: Unusable, speculative (age/identity), or contradicts the image.

Return ONLY valid compact JSON with this exact structure:
{{
  "items": [
    {{"idx": 1, "rating": <int 0-10>, "rank": <1|2|3>, "justification": "<short reason>", "issues": ["<bullet>", ...]}},
    {{"idx": 2, "rating": <int 0-10>, "rank": <1|2|3>, "justification": "<short reason>", "issues": ["<bullet>", ...]}},
    {{"idx": 3, "rating": <int 0-10>, "rank": <1|2|3>, "justification": "<short reason>", "issues": ["<bullet>", ...]}}
  ],
  "overall_notes": "<one- or two-sentence comparison across all three>"
}}

DESCRIPTIONS:
[1] {descriptions[0]}
[2] {descriptions[1]}
[3] {descriptions[2]}
""".strip()

    judged_text = gemini_text_from_image(judge_prompt, image_path)

    # Build output text file (exactly raw JSON output)
    out_lines = [f"Image: {image_path}"]
    out_lines.append("\n=== DESCRIPTIONS ===")
    for i, d in enumerate(descriptions, 1):
        out_lines.append(f"\n[{i}] {d}")
    out_lines.append("\n=== JUDGMENTS (comparative, single call) ===")
    out_lines.append("\n" + judged_text)

    # Save to timestamped file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    img_name = os.path.splitext(os.path.basename(image_path))[0]
    out_file = f"{timestamp}_{img_name}.txt"
    with open(out_file, "w") as f:
        f.write("\n".join(out_lines))

    print(f"\nResults saved to {out_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <image_path>")
        sys.exit(1)
    run(sys.argv[1])
