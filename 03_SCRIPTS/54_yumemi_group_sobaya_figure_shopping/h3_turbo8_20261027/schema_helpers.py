import re

def _t_schema(info, cls, *inputs):
    assert cls in info, (f"{cls} がこのComfyUIに無い — 更新で名前が変わった可能性。"
                         f" TURBO_8STEP=False で従来の20stepに戻せる")
    spec = info[cls].get("input", {})
    allsp = {**(spec.get("required") or {}), **(spec.get("optional") or {})}
    got = {}
    for pat in inputs:
        hit = sorted((n for n in allsp if re.search(pat, n, re.I)), key=len)
        assert hit, f"{cls}: 入力 {pat} が無い（実機の入力: {sorted(allsp)}）— TURBO_8STEP=False で回避できる"
        got[pat] = hit[0]
    return allsp, got


def _t_defaults(allsp, out):
    # 必須入力は既定値があっても省略できない（API形式のpromptにはフロントの既定が入らない）
    for name, sp in allsp.items():
        if name in out or not isinstance(sp, (list, tuple)) or not sp:
            continue
        typ, opts = sp[0], (sp[1] if len(sp) > 1 and isinstance(sp[1], dict) else {})
        if isinstance(typ, list):
            out[name] = opts.get("default", typ[0] if typ else None)
        elif isinstance(typ, str) and typ in ("INT", "FLOAT", "STRING", "BOOLEAN") and "default" in opts:
            out[name] = opts["default"]
    return out



