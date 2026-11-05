#!/usr/bin/env python3
"""Generate the Flatcap 2.0 files for Windows Terminal.

    python3 scripts/build.py              # write the JSON files and the generated README blocks
    python3 scripts/build.py --check      # fail if any generated output is stale
    python3 scripts/build.py --sync       # refresh src/theme.json from ../00-Flatcap, then rebuild
    python3 scripts/build.py --contrast   # print the contrast report (ANSI x background, selection, cursor)
    python3 scripts/build.py --schema F   # also validate against the official WT schema file F
                                          # (needs the optional `jsonschema` package; see README)

Input  : src/theme.json, a versioned copy of the Flatcap 2.0 core (the only source of values).
Outputs: flatcap-fragment.json   color schemes only, for Windows Terminal JSON fragment extensions
         flatcap-settings.json   color schemes + window themes, to paste into settings.json
         README.md               only the blocks between <!-- build:NAME --> markers

No hex value is written by hand in this file: every color is resolved from a Flatcap role.
Python 3.10+, standard library only. Output is deterministic.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "src" / "theme.json"
README = ROOT / "README.md"
UPSTREAM = (ROOT / ".." / "00-Flatcap" / "src" / "theme.json").resolve()
SCHEMA_URL = "https://aka.ms/terminal-profiles-schema"

MODES = ("slate", "daylight")
SCHEME_NAME = {"slate": "Flatcap Slate", "daylight": "Flatcap Daylight"}
THEME_NAME = SCHEME_NAME  # separate namespaces in Windows Terminal; same names on purpose
APP_THEME = {"slate": "dark", "daylight": "light"}
OUT_FRAGMENT = ROOT / "flatcap-fragment.json"
OUT_SETTINGS = ROOT / "flatcap-settings.json"

# ---------------------------------------------------------------------------
# Mapping tables. Roles only; hex values come from src/theme.json.
# Windows Terminal has no selection foreground: text keeps its own color on
# top of selectionBackground (see "Selection" in the README).
# ---------------------------------------------------------------------------

# (scheme key, role, intent)
FIELDS = [
    ("background", "bg.canvas", "Main area."),
    ("foreground", "text.primary", "Content text."),
    ("cursorColor", "accent.fg",
     "Text cursor. Not focus.ring (focus is independent of the cursor); the interaction accent keeps it quiet and visible."),
    ("selectionBackground", "selection.bg", "Text selection. The pair partner selection.fg cannot be expressed."),
]

# (scheme key, ANSI index, Slate role, Daylight role, intent)
# Rule 1: the six hues keep their meaning (red=danger, green=success, yellow=warning,
#         blue=interaction/info, purple=number/literal, cyan=function) and never cycle data.*.
# Rule 2: the core has no "bright" tier. Where a role with the same hue and a stronger step
#         exists it is used (blue); otherwise bright repeats the normal role instead of inventing
#         a value. Proposal for the core is in the README / delivery notes.
# Rule 3: black (0) and brightWhite (15) follow luminance, not role identity. Programs use them as block
#         backgrounds and as text on colored blocks, so black stays dark and brightWhite stays light in both modes.
# Rule 4: white (7) is readable ink in both modes (text.secondary). TUIs (bottom/ratatui Color::Gray,
#         htop, mc, lazygit) use it as their ordinary text color, so it must read on the canvas. It is
#         therefore not a light block color in Daylight; on dark ANSI backgrounds in Daylight use brightWhite.
ANSI = [
    ("black", 0, "border.subtle", "text.primary",
     "Dark neutral. Slate: lifted just enough to stay visible as a block on the canvas; Daylight: ink."),
    ("red", 1, "danger.fg", "danger.fg", "Errors, deletions."),
    ("green", 2, "success.fg", "success.fg", "Success, additions."),
    ("yellow", 3, "warning.fg", "warning.fg", "Warnings."),
    ("blue", 4, "accent.fg", "accent.fg", "Directories, links, information. Equal in value to info.fg and syntax.keyword."),
    ("purple", 5, "syntax.number", "syntax.number", "ANSI magenta: numbers, literals."),
    ("cyan", 6, "syntax.function", "syntax.function", "Functions, secondary identifiers."),
    ("white", 7, "text.secondary", "text.secondary",
     "Common TUI text (ratatui Color::Gray, htop, mc). Readable ink in both modes: secondary text, not a block color."),
    ("brightBlack", 8, "text.muted", "text.muted",
     "Dimmed text: autosuggestions, comments, metadata. Equal in value to syntax.comment."),
    ("brightRed", 9, "danger.fg", "danger.fg", "No stronger red in the core: repeats red."),
    ("brightGreen", 10, "success.fg", "success.fg", "No stronger green in the core: repeats green."),
    ("brightYellow", 11, "warning.fg", "warning.fg", "No stronger yellow in the core: repeats yellow."),
    ("brightBlue", 12, "accent.hover", "accent.hover",
     "Stronger step of the accent ramp (lighter in Slate, darker in Daylight: always more contrast)."),
    ("brightPurple", 13, "syntax.number", "syntax.number", "No stronger purple in the core: repeats purple."),
    ("brightCyan", 14, "syntax.function", "syntax.function", "No stronger cyan in the core: repeats cyan."),
    ("brightWhite", 15, "text.primary", "bg.raised",
     "Emphasized light neutral. Slate: primary ink; Daylight: the raised (white) surface."),
]
ANSI_KEYS = [a[0] for a in ANSI]
HUES = ("red", "green", "yellow", "blue", "purple", "cyan")
HUE_KEYS = [k for h in HUES for k in (h, "bright" + h[0].upper() + h[1:])]

# Window theme (WT "themes"). Values are roles, or the two special WT keywords.
# (dotted path, role or keyword, intent)
THEME_FIELDS = [
    ("window.frame", "border.control", "Active window border (Windows 11)."),
    ("window.unfocusedFrame", "border.subtle", "Inactive window border (Windows 11)."),
    ("tabRow.background", "bg.surface", "Tab row is navigation chrome."),
    ("tabRow.unfocusedBackground", "bg.surface", "Unchanged when the window is inactive."),
    ("tab.background", "terminalBackground", "Active tab joins the pane it controls (WT keyword, not a hex)."),
    ("tab.unfocusedBackground", "bg.surface", "Inactive tabs sit on the tab row."),
]
WT_KEYWORDS = {"terminalBackground", "accent"}

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load() -> dict:
    return json.loads(THEME.read_text(encoding="utf-8"))


def resolve(theme: dict, mode: str, role: str) -> str:
    if role in WT_KEYWORDS:
        return role
    return theme["themes"][mode][role]


def ansi_role(mode: str, key: str) -> str:
    for k, _i, s, d, _n in ANSI:
        if k == key:
            return s if mode == "slate" else d
    raise KeyError(key)


def scheme(theme: dict, mode: str) -> dict:
    out: dict[str, str] = {"name": SCHEME_NAME[mode]}
    for key, role, _ in FIELDS:
        out[key] = resolve(theme, mode, role)
    for key in ANSI_KEYS:
        out[key] = resolve(theme, mode, ansi_role(mode, key))
    return out


def window_theme(theme: dict, mode: str) -> dict:
    out: dict = {"name": THEME_NAME[mode], "window": {"applicationTheme": APP_THEME[mode]}}
    for path, role, _ in THEME_FIELDS:
        group, key = path.split(".")
        out.setdefault(group, {})[key] = resolve(theme, mode, role)
    return {k: out[k] for k in ("name", "tab", "tabRow", "window")}


def families(stack: str) -> list[str]:
    return re.findall(r'"([^"]+)"', stack)


def rem_to_px(value: str) -> float:
    assert value.endswith("rem"), value
    return float(value[:-3]) * 16


def fmt_num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else f"{x:g}"


def fonts(theme: dict) -> dict:
    code = families(theme["typography"]["font.code"])
    literal = families(theme["typography"]["font.literal"])
    px = rem_to_px(theme["typography"]["font.size.code"])
    return {"face": code[0], "face_nf": code[1], "mono": literal[0], "mono_nf": literal[1],
            "size_pt": round(px * 0.75, 2), "size_px": px}


def pair() -> dict:
    return {"dark": SCHEME_NAME["slate"], "light": SCHEME_NAME["daylight"]}


def dumps(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def fragment_doc(theme: dict) -> dict:
    return {"schemes": [scheme(theme, m) for m in MODES]}


def settings_doc(theme: dict) -> dict:
    return {"$schema": SCHEMA_URL,
            "schemes": [scheme(theme, m) for m in MODES],
            "themes": [window_theme(theme, m) for m in MODES]}


def defaults_doc(theme: dict) -> dict:
    f = fonts(theme)
    size = fmt_num(f["size_pt"])
    pad = fmt_num(rem_to_px(theme["metrics"]["space.4"]))
    return {
        "theme": pair(),
        "profiles": {"defaults": {
            "colorScheme": pair(),
            "font": {"face": f["face"], "size": float(size) if "." in size else int(size)},
            "intenseTextStyle": "all",
            "cursorShape": "bar",
            "padding": pad,
        }},
    }


# ---------------------------------------------------------------------------
# Validation (structural; the official JSON schema can be added with --schema)
# ---------------------------------------------------------------------------
def validate(theme: dict) -> list[str]:
    errs: list[str] = []
    for mode in MODES:
        s = scheme(theme, mode)
        for key in [*ANSI_KEYS, "background", "foreground", "cursorColor", "selectionBackground"]:
            if not HEX.match(s.get(key, "")):
                errs.append(f"{s['name']}: {key} is not #rrggbb ({s.get(key)!r})")
        t = window_theme(theme, mode)
        for grp in ("tab", "tabRow", "window"):
            for k, v in t[grp].items():
                if k == "applicationTheme":
                    continue
                if not (HEX.match(v) or v in WT_KEYWORDS):
                    errs.append(f"theme {t['name']}: {grp}.{k} invalid ({v!r})")
    if [a[1] for a in ANSI] != list(range(16)):
        errs.append("ANSI table must cover indexes 0..15 in order")
    return errs


def validate_schema(schema_path: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return ["jsonschema is not installed (optional): pip install jsonschema"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    v = cls(schema, format_checker=cls.FORMAT_CHECKER)
    theme = load()
    errs = []
    # The schema describes a whole settings.json, so each fragment is wrapped in the
    # minimum a settings file needs (placeholder defaultProfile, empty profile list).
    base = {"defaultProfile": "{00000000-0000-0000-0000-000000000000}", "profiles": {"list": []}, "schemes": []}
    docs = {"flatcap-fragment.json": fragment_doc(theme), "flatcap-settings.json": settings_doc(theme),
            "README profile snippet": defaults_doc(theme)}
    for name, doc in docs.items():
        merged = {**base, **{k: val for k, val in doc.items() if k != "profiles"}}
        if "profiles" in doc:
            merged["profiles"] = {**base["profiles"], **doc["profiles"]}
        doc = merged
        for e in v.iter_errors(doc):
            errs.append(f"{name}: {'/'.join(map(str, e.absolute_path))}: {e.message[:160]}")
    return errs


# ---------------------------------------------------------------------------
# Contrast
# ---------------------------------------------------------------------------
def _lum(h: str) -> float:
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a: str, b: str) -> float:
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def analysis(theme: dict) -> dict:
    """Numbers shared by --contrast, the README and the preview tooling."""
    out = {}
    for mode in MODES:
        s = scheme(theme, mode)
        bg, sel = s["background"], s["selectionBackground"]
        out[mode] = {
            "scheme": s,
            "fg_bg": ratio(s["foreground"], bg),
            "cursor_bg": ratio(s["cursorColor"], bg),
            "sel_bg": ratio(sel, bg),
            "fg_sel": ratio(s["foreground"], sel),
            "ansi_bg": {k: ratio(s[k], bg) for k in ANSI_KEYS},
            "ansi_sel": {k: ratio(s[k], sel) for k in ANSI_KEYS},
            "cross": {f: {b: ratio(s[f], s[b]) for b in ANSI_KEYS} for f in ANSI_KEYS},
        }
    return out


def contrast_report(theme: dict) -> str:
    data = analysis(theme)
    L: list[str] = []
    for mode in MODES:
        d = data[mode]
        s = d["scheme"]
        L.append(f"[{s['name']}]  background {s['background']}  selection {s['selectionBackground']}")
        L.append(f"  foreground on background      {d['fg_bg']:6.2f}:1  (target 7)")
        L.append(f"  cursor on background          {d['cursor_bg']:6.2f}:1  (target 3)")
        L.append(f"  selection bg vs background    {d['sel_bg']:6.2f}:1  (info; no core target)")
        L.append(f"  foreground on selection       {d['fg_sel']:6.2f}:1  (target 4.5)")
        L.append("  ANSI as foreground:")
        L.append(f"    {'key':<13}{'hex':<9}{'on bg':>8}{'on sel':>8}  notes")
        for k in ANSI_KEYS:
            nb, ns = d["ansi_bg"][k], d["ansi_sel"][k]
            flags = []
            if k == "brightWhite" or (mode == "slate" and k == "black"):
                flags.append("neutral block color: used as background, not for reading on the canvas")
            else:
                if nb < 5:
                    flags.append("bg<5")
                if ns < 4.5:
                    flags.append("sel<4.5")
            L.append(f"    {k:<13}{s[k]:<9}{nb:8.2f}{ns:8.2f}  {'; '.join(flags)}")
        L.append("  Cross matrix (fg rows on bg columns, ratio):")
        L.append("    " + " " * 13 + "".join(f"{i:>6}" for i in range(16)))
        for f in ANSI_KEYS:
            L.append(f"    {f:<13}" + "".join(f"{d['cross'][f][b]:6.1f}" for b in ANSI_KEYS))
        L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# README generated blocks
# ---------------------------------------------------------------------------
def md_fields(theme: dict) -> str:
    rows = ["| Scheme field | Flatcap role | Slate | Daylight |", "| :--- | :--- | :--- | :--- |"]
    for key, role, _ in FIELDS:
        rows.append(f"| `{key}` | `{role}` | `{resolve(theme, 'slate', role)}` | `{resolve(theme, 'daylight', role)}` |")
    rows += ["", "| Window theme field | Flatcap role | Slate | Daylight |", "| :--- | :--- | :--- | :--- |",
             "| `window.applicationTheme` | (mode) | `dark` | `light` |"]
    for path, role, _ in THEME_FIELDS:
        s, d = resolve(theme, "slate", role), resolve(theme, "daylight", role)
        v = (lambda x: f"`{x}`")
        rows.append(f"| `{path}` | `{role}` | {v(s)} | {v(d)} |")
    return "\n".join(rows)


def md_ansi(theme: dict) -> str:
    data = analysis(theme)
    rows = ["| # | Key | Flatcap role | Slate | Daylight |", "| ---: | :--- | :--- | :--- | :--- |"]
    for key, idx, rs, rd, _ in ANSI:
        role = f"`{rs}`" if rs == rd else f"`{rs}` (Slate) · `{rd}` (Daylight)"
        s, d = data["slate"]["scheme"][key], data["daylight"]["scheme"][key]
        rows.append(f"| {idx} | `{key}` | {role} | `{s}` · {data['slate']['ansi_bg'][key]:.1f}:1 | "
                    f"`{d}` · {data['daylight']['ansi_bg'][key]:.1f}:1 |")
    return "\n".join(rows)


def md_contrast(theme: dict) -> str:
    D = analysis(theme)

    def cell(mode, v):
        return f"{v:.2f}:1"

    def mn(mode, table, keys):
        return min(D[mode][table][k] for k in keys)

    neutrals = ("black", "brightWhite")
    text_keys = [k for k in ANSI_KEYS if k not in neutrals]
    rows = ["| Pair | Slate | Daylight | Target | Result |", "| :--- | ---: | ---: | ---: | :--- |"]

    def row(label, sv, dv, target, ok_s, ok_d, note=""):
        res = "met" if ok_s and ok_d else ("not met" + (f": {note}" if note else ""))
        rows.append(f"| {label} | {sv:.2f}:1 | {dv:.2f}:1 | {target} | {res} |")

    row("`foreground` on `background`", D["slate"]["fg_bg"], D["daylight"]["fg_bg"], "7:1",
        D["slate"]["fg_bg"] >= 7, D["daylight"]["fg_bg"] >= 7)
    row("Hues (red…cyan, normal and bright) on `background`, lowest", mn("slate", "ansi_bg", HUE_KEYS),
        mn("daylight", "ansi_bg", HUE_KEYS), "5:1", mn("slate", "ansi_bg", HUE_KEYS) >= 5, mn("daylight", "ansi_bg", HUE_KEYS) >= 5)
    row("`brightBlack` (dimmed text) on `background`", D["slate"]["ansi_bg"]["brightBlack"],
        D["daylight"]["ansi_bg"]["brightBlack"], "5:1", D["slate"]["ansi_bg"]["brightBlack"] >= 5,
        D["daylight"]["ansi_bg"]["brightBlack"] >= 5)
    row("`cursorColor` on `background`", D["slate"]["cursor_bg"], D["daylight"]["cursor_bg"], "3:1",
        D["slate"]["cursor_bg"] >= 3, D["daylight"]["cursor_bg"] >= 3)
    row("`foreground` on `selectionBackground`", D["slate"]["fg_sel"], D["daylight"]["fg_sel"], "4.5:1",
        D["slate"]["fg_sel"] >= 4.5, D["daylight"]["fg_sel"] >= 4.5)
    sl, dl = mn("slate", "ansi_sel", text_keys), mn("daylight", "ansi_sel", text_keys)
    row("Hues and `brightBlack` on `selectionBackground`, lowest", sl, dl, "4.5:1", sl >= 4.5, dl >= 4.5,
        "see the selection note below")
    rows.append(f"| `selectionBackground` vs `background` | {D['slate']['sel_bg']:.2f}:1 | "
                f"{D['daylight']['sel_bg']:.2f}:1 | none | informational |")
    rows += ["", "Colors that fall short of 4.5:1 as text on `selectionBackground` (colors with equal values are grouped):", ""]
    for mode, label in (("slate", "Slate"), ("daylight", "Daylight")):
        groups: dict[str, list[str]] = {}
        for k in text_keys:
            if D[mode]["ansi_sel"][k] < 4.5:
                groups.setdefault(D[mode]["scheme"][k], []).append(k)
        items = ["/".join(f"`{k}`" for k in ks) + f" {D[mode]['ansi_sel'][ks[0]]:.2f}:1" for ks in groups.values()]
        rows.append(f"- {label}: " + "; ".join(items) + ".")
    rows += ["", "Text on ANSI background colors (`ESC[4Xm`), as ratio of the text color on that background:", "",
             "| Background | Slate: `black` | Slate: `brightWhite` | Daylight: `black` | Daylight: `brightWhite` |",
             "| :--- | ---: | ---: | ---: | ---: |"]
    for h in HUES:
        r = [f"`{h}`"]
        for mode in MODES:
            for fg in ("black", "brightWhite"):
                r.append(f"{D[mode]['cross'][fg][h]:.2f}:1")
        rows.append("| " + " | ".join(r) + " |")
    return "\n".join(rows)


def md_snippet(theme: dict) -> str:
    return "```json\n" + dumps(defaults_doc(theme)).rstrip("\n") + "\n```"


def md_json(theme: dict) -> str:
    doc = {"schemes": [scheme(theme, m) for m in MODES], "themes": [window_theme(theme, m) for m in MODES]}
    return "```json\n" + dumps(doc).rstrip("\n") + "\n```"


def md_fonts(theme: dict) -> str:
    f = fonts(theme)
    return (f"| Use | Family (exact) |\n| :--- | :--- |\n"
            f"| Default | `{f['face']}` |\n"
            f"| Prompts with icons (oh-my-posh, starship) | `{f['face_nf']}` |\n"
            f"| No ligatures (logs, literal output) | `{f['mono']}` |\n"
            f"| No ligatures, with icons | `{f['mono_nf']}` |\n\n"
            f"Starting size: {fmt_num(f['size_px'])} px from `font.size.code`, which is {fmt_num(f['size_pt'])} pt in "
            f"Windows Terminal (1 pt = 1.333 px at 100% scale).")


BLOCKS = {"fields": md_fields, "ansi": md_ansi, "contrast": md_contrast,
          "snippet": md_snippet, "json": md_json, "fonts": md_fonts}


def render_readme(theme: dict) -> str:
    text = README.read_text(encoding="utf-8")
    for name, fn in BLOCKS.items():
        pat = re.compile(rf"(<!-- build:{name} -->)\n.*?(<!-- /build:{name} -->)", re.S)
        if not pat.search(text):
            raise SystemExit(f"error: README.md is missing the build:{name} markers")
        text = pat.sub(lambda m: m.group(1) + "\n" + fn(theme) + "\n" + m.group(2), text)
    return text


# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if generated outputs are stale")
    ap.add_argument("--contrast", action="store_true", help="print the contrast report and exit")
    ap.add_argument("--sync", nargs="?", const=str(UPSTREAM), metavar="PATH",
                    help="copy theme.json from the core checkout (default ../00-Flatcap/src/theme.json)")
    ap.add_argument("--schema", metavar="FILE", help="also validate against the official WT schema file")
    args = ap.parse_args()

    if args.sync:
        src = Path(args.sync)
        if src.is_dir():
            src = src / "src" / "theme.json"
        if not src.is_file():
            print(f"error: {src} not found", file=sys.stderr)
            return 2
        shutil.copyfile(src, THEME)
        print(f"synced {src} -> {THEME.relative_to(ROOT)}")

    theme = load()
    if not str(theme.get("version", "")).startswith("2."):
        print(f"error: expected Flatcap 2.x theme.json, got {theme.get('version')}", file=sys.stderr)
        return 2
    errs = validate(theme)
    if args.schema:
        errs += validate_schema(Path(args.schema))
    if errs:
        print("\n".join("error: " + e for e in errs), file=sys.stderr)
        return 2
    if args.contrast:
        print(contrast_report(theme))
        return 0
    if UPSTREAM.is_file() and UPSTREAM.read_bytes() != THEME.read_bytes():
        print("note: src/theme.json differs from ../00-Flatcap (run --sync to refresh)", file=sys.stderr)

    outputs = {OUT_FRAGMENT: dumps(fragment_doc(theme)), OUT_SETTINGS: dumps(settings_doc(theme)),
               README: render_readme(theme)}
    stale = []
    for path, text in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                stale.append(path.name)
        else:
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.name}")
    if args.check:
        if stale:
            print("stale: " + ", ".join(stale) + " (run python3 scripts/build.py)", file=sys.stderr)
            return 1
        print("ok: generated files are up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
