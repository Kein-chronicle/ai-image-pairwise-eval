---
name: art-eval
description: Evaluate visual quality (game art, illustrations, UI, generated images) reliably against golden reference images - rubric levels instead of absolute scores, order-swapped pairwise comparison, and CLIP/DINO embedding similarity as a consistency gate. Use whenever you must judge if an asset is good enough, rank candidates, gate AI-generated art, or replace "looks fine to me" with a repeatable method.
---

# art-eval

This workflow prefers reference-based comparisons over uncalibrated absolute scores. Both absolute scoring and pairwise ranking can be inconsistent; neither is treated as objective quality measurement. Use:

1. **Find the golden reference** - the image a human approved as "this is the target", per style context (battle vs
   illustration). None? Say so, use the written art bible as a stand-in, and mark confidence **low**.
2. **Rubric with discrete levels** (excellent / good / fair / poor + concrete evidence), never numbers:
   style match - anatomy/structure (hands, fingers, proportions, symmetry, joints; the most common generated-art failure) -
   concept match (canon, props, world) - finish/render (lighting, artifacts, mush) - character consistency.
3. **Pairwise comparison for multiple candidates**: "which is closer to the reference, A or B?" Ask twice with the order
   **swapped**; if the answer flips it is a **tie** (position bias). `scripts/pairwise.py` resolves the pair.
4. **Embedding similarity** (optional, `scripts/art_similarity.py`, needs `torch`, `open_clip`, optionally `transformers`):
   cosine similarity candidate vs reference set. Calibrate thresholds on labeled examples for the chosen model and preprocessing; no universal cutoff is provided.
   It is a proxy for *resemblance*, not beauty and not anatomy.
5. **Structured verdict**:
```
[art-eval] target: <file> / reference: <golden | none (confidence low)>
- style match: <level> - <evidence>
- anatomy: <level> - <evidence>
- concept: <level> - <evidence>
- render: <level> - <evidence>
- consistency: CLIP <value> (threshold <t>, pass|fail)
-> PASS | REVISE (which item is fair or below, what to change) | REJECT
-> The final aesthetic go/no-go is a human's. This gate removes below-standard work; it does not create excellence.
```

## Gate rules (defaults)
- style or anatomy **poor** -> REJECT (regenerate). Any item **fair** -> REVISE with specific edits.
- CLIP below threshold -> REVISE. All good+ and consistency pass -> PASS, subject to human approval.

## Honest limits
Embedding similarity is not quality. A bad reference makes a bad gate - establishing golden references is the highest-leverage
human task. This method keeps a reproducible *floor*.

Runtime status: beta. Current tests cover pairwise decision logic and Python syntax only; embedding inference and model downloads have not been validated in this release. `art_similarity.py` exits 1 when the mean similarity is below `--threshold` (default 0.85, a starting point), 2 for bad arguments, 3 when it could not measure.

Runtime dependency: install `requirements.txt` with `python3 -m pip install -r requirements.txt`. Pillow must be at least 12.3.0; optional model dependencies listed above are separate.
