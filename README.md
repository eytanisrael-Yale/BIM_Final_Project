main.py is a way we can test different prompts to see which are more accurate and succinct 

EXAMPLE:
Image: ../ex1.png

=== DESCRIPTIONS ===

[1] Hey you, in the light blue strapless top.

[2] Hey you, in the light blue strapless top and brown sandals, between the blue dress and the Hawaiian shirt.

[3] Hey you, in the light blue strapless top and denim shorts.

=== JUDGMENTS (comparative, single call) ===

```json
{
  "items": [
    {
      "idx": 1,
      "rating": 10,
      "rank": 1,
      "justification": "Unambiguously identifies the individual using the most distinctive and unique clothing item, and is maximally brief.",
      "issues": []
    },
    {
      "idx": 2,
      "rating": 8,
      "rank": 3,
      "justification": "Though highly descriptive and accurate, it includes multiple details (sandals, positional context) that are not strictly necessary for unambiguous identification, making it less brief than possible.",
      "issues": [
        "Contains extra words beyond what is minimally required for unambiguous identification."
      ]
    },
    {
      "idx": 3,
      "rating": 9,
      "rank": 2,
      "justification": "Clearly identifies the individual, but the addition of 'and denim shorts' is not strictly necessary for unambiguous identification given the unique top, making it slightly less brief.",
      "issues": [
        "Contains extra words beyond what is minimally required for unambiguous identification."
      ]
    }
  ],
  "overall_notes": "Description 1 is superior as it leverages the most unique identifier (the top) to achieve unambiguous identification with maximal brevity. Descriptions 2 and 3, while accurate, add superfluous details beyond what is minimally required, making them less brief."
}
```
