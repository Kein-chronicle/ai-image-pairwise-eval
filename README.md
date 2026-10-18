# ai-image-pairwise-eval

**Evaluate AI-generated art without vibes: position-bias-safe pairwise judging and similarity to reference images with open_clip.**

[![test](https://github.com/Kein-chronicle/ai-image-pairwise-eval/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/ai-image-pairwise-eval/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg)

## Why

An LLM that says "this looks better" mostly says "this was shown first". Ask twice with the order swapped and treat a flipped answer as a tie. For references, measure embedding similarity instead of describing.

> **Status: beta (embedding inference untested).** Beta: only the pairwise logic is tested; model inference is not exercised by the tests. Embedding similarity is not a quality score.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/ai-image-pairwise-eval.git ~/.claude/skills/art-eval
```

For a single project, clone into `<project>/.claude/skills/art-eval` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/ai-image-pairwise-eval.git
cd ai-image-pairwise-eval
```

**Requires:** Python 3.10+, Pillow, torch, pillow, open_clip_torch (optional, for art_similarity.py).

Use the security-patched Pillow runtime:

```sh
python3 -m pip install -r requirements.txt
```

## Quick start

Resolve a pairwise judgement:

```console
$ bash examples/demo.sh
# Position bias: ask the judge twice with the two images swapped.
# Each answer is the POSITION picked (first|second). Consistent picks mean a real preference:
$ python3 scripts/pairwise.py first second
A
[exit 0]

# Picking 'first' both times means the judge likes position, not the image: a tie
$ python3 scripts/pairwise.py first first
TIE (answer flipped with order: position bias)
[exit 1]

# Embedding similarity to references needs:  pip install torch pillow open_clip_torch
$ python3 scripts/art_similarity.py
UNMEASURED: missing dependency (No module named 'torch'); pip install torch pillow open_clip_torch
[exit 3]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/pairwise.py first second   # the position picked in run 1 (order A,B) and run 2 (order B,A)
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- `pairwise.py <answer_run1> <answer_run2>`: each answer is the position picked (`first|second`). Consistent picks name a winner; flipped answers are a tie.
- `art_similarity.py`: similarity to a reference set with open_clip; reports `UNMEASURED` (exit 3) when the model dependencies are missing.

## Limits

- Beta: only the pairwise logic is tested; model inference is not exercised by the tests.
- Embedding similarity is not a quality score.
- On first use `art_similarity.py` downloads model weights from public model hubs; pin revisions or mirror them if you need a fixed supply chain.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **OpenCLIP**: the embedding model this builds on

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**canvas-render-pixel-gate**](https://github.com/Kein-chronicle/canvas-render-pixel-gate): Detect grey-box screenshots: measure unique colors and flat-fill share of a rendered game canvas, and refuse to pass what it could not measure.
- [**web-game-asset-reality-check**](https://github.com/Kein-chronicle/web-game-asset-reality-check): Catch web-game bugs the type checker can't: fonts that are declared but not shipped, runtime CDN dependencies, and page errors from headless Chromium.
- [**ffmpeg-video-qa-gates**](https://github.com/Kein-chronicle/ffmpeg-video-qa-gates): Machine QA for short videos with ffmpeg: frozen frames, dead air, loudness, true peak, size, a busy opening, and readable subtitle timing.

## Development

```sh
bash tests/test.sh
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: generative-ai, image-generation, evaluation, clip, open-clip, art, game-art, claude-skills</sub>
