#!/usr/bin/env python3
"""art-eval quantitative layer: embedding similarity (0..1) between a candidate and golden references.
CLIP = semantics/style, DINO = subject/texture. VLMs cannot score absolutely, so consistency is measured by cosine similarity.
usage:
  art_similarity.py --candidate cand.png --ref ref1.png ref2.png [--dino] [--threshold 0.85]
  art_similarity.py --a A.png --b B.png
needs: torch, pillow, open_clip_torch (and transformers for --dino). First use downloads model weights from public model hubs.
exit 0 measured and (for --candidate) the mean similarity reaches the threshold | 1 below the threshold | 2 bad arguments | 3 could not measure
(missing dependencies, unreadable image). --a/--b only prints the similarity and exits 0. The threshold is a starting point, not a universal cutoff.
"""
import argparse
import json
import os
import sys

try:
    import torch
    from PIL import Image
    import open_clip  # noqa: F401  (imported here so a missing package is exit 3, not a traceback later)
except ImportError as e:
    print(f"UNMEASURED: missing dependency ({e}); pip install torch pillow open_clip_torch"); sys.exit(3)

CLIP_MODEL = "ViT-B-32"
CLIP_PRETRAIN = "laion2b_s34b_b79k"


def _device():
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def _clip_embedder():
    import open_clip
    dev = _device()
    model, _, preprocess = open_clip.create_model_and_transforms(CLIP_MODEL, pretrained=CLIP_PRETRAIN)
    model = model.to(dev).eval()

    @torch.no_grad()
    def embed(path):
        img = preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(dev)
        feat = model.encode_image(img)
        return feat / feat.norm(dim=-1, keepdim=True)

    return embed


def _dino_embedder():
    from transformers import AutoImageProcessor, AutoModel
    dev = _device()
    proc = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
    model = AutoModel.from_pretrained("facebook/dinov2-base").to(dev).eval()

    @torch.no_grad()
    def embed(path):
        img = Image.open(path).convert("RGB")
        inputs = proc(images=img, return_tensors="pt").to(dev)
        out = model(**inputs)
        feat = out.last_hidden_state[:, 0]  # CLS token
        return feat / feat.norm(dim=-1, keepdim=True)

    return embed


def _cos(a, b):
    return float((a @ b.T).item())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate")
    ap.add_argument("--ref", nargs="+", default=[])
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--dino", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.85)
    args = ap.parse_args()

    if not (args.a and args.b) and not (args.candidate and args.ref):
        print("need --candidate and at least one --ref (or --a --b)", file=sys.stderr); sys.exit(2)
    missing = [p for p in ([args.a, args.b] if args.a and args.b else [args.candidate] + args.ref) if not os.path.isfile(p)]
    if missing: print(f"UNMEASURED: image not found: {missing[0]}"); sys.exit(3)            # validated before any model is loaded or downloaded
    try:
        _run(args)
    except ImportError as e:
        print(f"UNMEASURED: missing dependency ({e})"); sys.exit(3)
    except OSError as e:
        print(f"UNMEASURED: cannot read an image or model ({type(e).__name__}: {e})"); sys.exit(3)


def _run(args):
    clip_embed = _clip_embedder()
    dino_embed = _dino_embedder() if args.dino else None

    if args.a and args.b:
        out = {"mode": "pairwise", "a": args.a, "b": args.b,
               "clip_sim": round(_cos(clip_embed(args.a), clip_embed(args.b)), 4)}
        if dino_embed:
            out["dino_sim"] = round(_cos(dino_embed(args.a), dino_embed(args.b)), 4)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    c = clip_embed(args.candidate)
    per_ref = [{"ref": r, "clip_sim": round(_cos(c, clip_embed(r)), 4)} for r in args.ref]
    mean_clip = round(sum(x["clip_sim"] for x in per_ref) / len(per_ref), 4)
    out = {"mode": "candidate_vs_refs", "candidate": args.candidate,
           "clip_model": f"{CLIP_MODEL}/{CLIP_PRETRAIN}",
           "per_ref": per_ref, "mean_clip": mean_clip,
           "threshold": args.threshold, "pass": mean_clip >= args.threshold}
    if dino_embed:
        cd = dino_embed(args.candidate)
        dino_vals = [round(_cos(cd, dino_embed(r)), 4) for r in args.ref]
        out["mean_dino"] = round(sum(dino_vals) / len(dino_vals), 4)
        out["per_ref_dino"] = dino_vals
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["pass"] else 1)


if __name__ == "__main__":
    main()
