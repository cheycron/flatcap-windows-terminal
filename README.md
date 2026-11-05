# Flatcap for Windows Terminal

![Version](https://img.shields.io/badge/version-2.0.0-blueviolet) ![Windows Terminal](https://img.shields.io/badge/Windows%20Terminal-1.17%2B-blue) ![License](https://img.shields.io/badge/license-MIT-blue)

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/screenshot-slate.png">
    <source media="(prefers-color-scheme: light)" srcset="images/screenshot-daylight.png">
    <img src="images/screenshot-slate.png" alt="Windows Terminal with Flatcap running bottom: CPU, memory and network graphs, temperature and disk tables, and a process list with the selected row highlighted" width="100%">
  </picture>
</p>

<p align="center"><sub>Slate or Daylight is shown to match your GitHub appearance.</sub></p>

**Flatcap for Windows Terminal** brings the Flatcap visual system to your shell: matte graphite or soft daylight surfaces, one mineral-blue accent, the 16 ANSI colors tied to what they mean, and Cascadia Code.

> The interface organizes. Content takes the foreground. Color informs.

It ships two color schemes, **Flatcap Slate** (dark) and **Flatcap Daylight** (light), plus matching window themes for the tab row and window border. Windows Terminal can switch between them when Windows does.

## Quiet precision

[Flatcap](https://github.com/cheycron/flat-cap-theme) is a semantic visual system for focused work. Colors are named for **what they do**, not for how they look, and the two modes share roles rather than identical values: Daylight is not an inverted Slate.

- **Output first.** Red is an error, green is success, yellow is a warning, blue is information. They are not recycled as decoration.
- **Dim means dim.** Autosuggestions and comments use a quiet, still-readable tone, not a near-invisible one.
- **Matte.** No transparency, acrylic or glow. The terminal sits on the same canvas as the rest of Flatcap.
- **Both modes tuned.** Each mode is checked on its own background, not derived by inversion.

## What is in the box

| File | Use it when |
| :--- | :--- |
| `flatcap-fragment.json` | You want the two color schemes installed **without editing `settings.json`** (recommended). |
| `flatcap-settings.json` | You prefer to paste the color schemes, and also want the **window themes** (tab row, window border). |

Both are generated from the Flatcap 2.0 tokens; see [How it is built](#how-it-is-built).

## Install

### Option A: JSON fragment (recommended)

Windows Terminal reads **JSON fragment extensions** from a folder and adds their color schemes to its settings. Nothing in your `settings.json` changes, and updating Flatcap later means replacing one file.

In PowerShell:

```powershell
$dir = "$env:LOCALAPPDATA\Microsoft\Windows Terminal\Fragments\Flatcap"
New-Item -ItemType Directory -Force $dir | Out-Null
Invoke-WebRequest https://raw.githubusercontent.com/cheycron/flatcap-windows-terminal/main/flatcap-fragment.json -OutFile "$dir\flatcap.json"
```

Use `C:\ProgramData\Microsoft\Windows Terminal\Fragments\Flatcap` instead to install for every user. Then open the Terminal settings, or restart it: **Flatcap Slate** and **Flatcap Daylight** appear under **Color schemes**.

A fragment can only add color schemes and profiles. It cannot add window themes or change your defaults, so continue with [Use it](#use-it). To tweak a fragment scheme, copy it into your own `schemes` array first.

### Option B: paste into `settings.json`

> [!WARNING]
> Do not replace your whole `settings.json` with `flatcap-settings.json`. Copy only the entries described below.

1. Open the Terminal settings and click **Open JSON file** (bottom left).
2. From `flatcap-settings.json`, copy the two objects of the `schemes` array into your own `schemes` array.
3. Optional, for the tab row and window border: copy the two objects of the `themes` array into your `themes` array (add the array at the top level if you do not have one). Window themes can only be edited in JSON.

<details>
<summary>The generated JSON, ready to copy</summary>

<!-- build:json -->
```json
{
  "schemes": [
    {
      "name": "Flatcap Slate",
      "background": "#191D22",
      "foreground": "#D5DBE3",
      "cursorColor": "#9BBFDF",
      "selectionBackground": "#3C546B",
      "black": "#3D4652",
      "red": "#E2A0A5",
      "green": "#9FC3AD",
      "yellow": "#D8BC87",
      "blue": "#9BBFDF",
      "purple": "#B6AED5",
      "cyan": "#ABC9CB",
      "white": "#AEB8C4",
      "brightBlack": "#A7B3C2",
      "brightRed": "#E2A0A5",
      "brightGreen": "#9FC3AD",
      "brightYellow": "#D8BC87",
      "brightBlue": "#ACCCE7",
      "brightPurple": "#B6AED5",
      "brightCyan": "#ABC9CB",
      "brightWhite": "#D5DBE3"
    },
    {
      "name": "Flatcap Daylight",
      "background": "#F3F5F7",
      "foreground": "#28313B",
      "cursorColor": "#285D85",
      "selectionBackground": "#C8DDF0",
      "black": "#28313B",
      "red": "#A43F4A",
      "green": "#32664D",
      "yellow": "#765319",
      "blue": "#285D85",
      "purple": "#68598C",
      "cyan": "#306770",
      "white": "#465463",
      "brightBlack": "#536273",
      "brightRed": "#A43F4A",
      "brightGreen": "#32664D",
      "brightYellow": "#765319",
      "brightBlue": "#214F73",
      "brightPurple": "#68598C",
      "brightCyan": "#306770",
      "brightWhite": "#FFFFFF"
    }
  ],
  "themes": [
    {
      "name": "Flatcap Slate",
      "tab": {
        "background": "terminalBackground",
        "unfocusedBackground": "#20252B"
      },
      "tabRow": {
        "background": "#20252B",
        "unfocusedBackground": "#20252B"
      },
      "window": {
        "applicationTheme": "dark",
        "frame": "#8593A5",
        "unfocusedFrame": "#3D4652"
      }
    },
    {
      "name": "Flatcap Daylight",
      "tab": {
        "background": "terminalBackground",
        "unfocusedBackground": "#FAFBFC"
      },
      "tabRow": {
        "background": "#FAFBFC",
        "unfocusedBackground": "#FAFBFC"
      },
      "window": {
        "applicationTheme": "light",
        "frame": "#6C7A89",
        "unfocusedFrame": "#D2D9E0"
      }
    }
  ]
}
```
<!-- /build:json -->

</details>

## Use it

### Follow the system light/dark setting

This is the recommended setup. Put the following in `settings.json`; it also applies Cascadia Code, a matching intense-text style and a 4px-grid padding to every profile:

<!-- build:snippet -->
```json
{
  "theme": {
    "dark": "Flatcap Slate",
    "light": "Flatcap Daylight"
  },
  "profiles": {
    "defaults": {
      "colorScheme": {
        "dark": "Flatcap Slate",
        "light": "Flatcap Daylight"
      },
      "font": {
        "face": "Cascadia Code",
        "size": 11.25
      },
      "intenseTextStyle": "all",
      "cursorShape": "bar",
      "padding": "16"
    }
  }
}
```
<!-- /build:snippet -->

How it works:

- `theme` picks the window theme from the Windows appearance. Each Flatcap window theme sets its application theme (dark or light).
- `colorScheme` with `dark`/`light` follows the **application theme** of the selected window theme. That is why the two are used together. If you use another window theme fixed to dark, the color scheme will always be the dark one.
- Prefer to keep the stock window chrome? Leave out `theme` or set it to `"system"`: the scheme pair still follows Windows.
- **Installed with Option A only?** The window themes named in `theme` do not exist yet. Replace that line with `"theme": "system"` (or add the themes as in Option B) and keep the rest.

### One mode, always

Set `"colorScheme": "Flatcap Slate"` or `"colorScheme": "Flatcap Daylight"` in a single profile, or inside `profiles.defaults` for every profile. Set `"theme"` to the window theme with the same name to match the tab row.

### Coming from Flatcap 1.x

Version 2.0 is a breaking change: the Nord-derived v1 palette is replaced by Flatcap 2.0 roles. The scheme previously named `Flatcap` no longer exists, and there is no alias on purpose: a second entry that looks like Slate but is not named for its mode would be ambiguous in the picker.

1. Delete the old `Flatcap` object from your `schemes` array.
2. Replace `"colorScheme": "Flatcap"` with `"Flatcap Slate"` (or the light/dark pair above).

## Fonts

Flatcap starts from **Cascadia Code**, which ships with Windows Terminal. Nerd Font builds are an option for prompts with icons, never a requirement.

<!-- build:fonts -->
| Use | Family (exact) |
| :--- | :--- |
| Default | `Cascadia Code` |
| Prompts with icons (oh-my-posh, starship) | `Cascadia Code NF` |
| No ligatures (logs, literal output) | `Cascadia Mono` |
| No ligatures, with icons | `Cascadia Mono NF` |

Starting size: 15 px from `font.size.code`, which is 11.25 pt in Windows Terminal (1 pt = 1.333 px at 100% scale).
<!-- /build:fonts -->

Notes:

- Use the **exact installed family name**. `Cascadia Code NF` (from the Cascadia releases) and the Nerd Fonts build `CaskaydiaCove Nerd Font Mono` are different families and are not interchangeable.
- Windows Terminal has no per-region ligature control. If ligatures hurt when reading logs or hashes, switch the profile to the Mono family, or turn them off with `"font": { "features": { "calt": 0 } }`.
- The line height is left at the Windows Terminal default. The Flatcap code line height suits editors; a terminal needs contiguous cells for box drawing and full-screen programs.

## Mapping: Flatcap roles to the scheme

Colors are resolved by **meaning**, never by position or by nearest hex. Every value below comes from [`src/theme.json`](src/theme.json).

<!-- build:fields -->
| Scheme field | Flatcap role | Slate | Daylight |
| :--- | :--- | :--- | :--- |
| `background` | `bg.canvas` | `#191D22` | `#F3F5F7` |
| `foreground` | `text.primary` | `#D5DBE3` | `#28313B` |
| `cursorColor` | `accent.fg` | `#9BBFDF` | `#285D85` |
| `selectionBackground` | `selection.bg` | `#3C546B` | `#C8DDF0` |

| Window theme field | Flatcap role | Slate | Daylight |
| :--- | :--- | :--- | :--- |
| `window.applicationTheme` | (mode) | `dark` | `light` |
| `window.frame` | `border.control` | `#8593A5` | `#6C7A89` |
| `window.unfocusedFrame` | `border.subtle` | `#3D4652` | `#D2D9E0` |
| `tabRow.background` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `tabRow.unfocusedBackground` | `bg.surface` | `#20252B` | `#FAFBFC` |
| `tab.background` | `terminalBackground` | `terminalBackground` | `terminalBackground` |
| `tab.unfocusedBackground` | `bg.surface` | `#20252B` | `#FAFBFC` |
<!-- /build:fields -->

### The 16 ANSI colors

The ratio is the color as text on the scheme `background`.

<!-- build:ansi -->
| # | Key | Flatcap role | Slate | Daylight |
| ---: | :--- | :--- | :--- | :--- |
| 0 | `black` | `border.subtle` (Slate) · `text.primary` (Daylight) | `#3D4652` · 1.8:1 | `#28313B` · 12.1:1 |
| 1 | `red` | `danger.fg` | `#E2A0A5` · 7.9:1 | `#A43F4A` · 5.7:1 |
| 2 | `green` | `success.fg` | `#9FC3AD` · 8.8:1 | `#32664D` · 6.1:1 |
| 3 | `yellow` | `warning.fg` | `#D8BC87` · 9.2:1 | `#765319` · 6.4:1 |
| 4 | `blue` | `accent.fg` | `#9BBFDF` · 8.8:1 | `#285D85` · 6.4:1 |
| 5 | `purple` | `syntax.number` | `#B6AED5` · 8.1:1 | `#68598C` · 5.7:1 |
| 6 | `cyan` | `syntax.function` | `#ABC9CB` · 9.6:1 | `#306770` · 5.8:1 |
| 7 | `white` | `text.secondary` | `#AEB8C4` · 8.4:1 | `#465463` · 7.1:1 |
| 8 | `brightBlack` | `text.muted` | `#A7B3C2` · 8.0:1 | `#536273` · 5.7:1 |
| 9 | `brightRed` | `danger.fg` | `#E2A0A5` · 7.9:1 | `#A43F4A` · 5.7:1 |
| 10 | `brightGreen` | `success.fg` | `#9FC3AD` · 8.8:1 | `#32664D` · 6.1:1 |
| 11 | `brightYellow` | `warning.fg` | `#D8BC87` · 9.2:1 | `#765319` · 6.4:1 |
| 12 | `brightBlue` | `accent.hover` | `#ACCCE7` · 10.1:1 | `#214F73` · 7.9:1 |
| 13 | `brightPurple` | `syntax.number` | `#B6AED5` · 8.1:1 | `#68598C` · 5.7:1 |
| 14 | `brightCyan` | `syntax.function` | `#ABC9CB` · 9.6:1 | `#306770` · 5.8:1 |
| 15 | `brightWhite` | `text.primary` (Slate) · `bg.raised` (Daylight) | `#D5DBE3` · 12.2:1 | `#FFFFFF` · 1.1:1 |
<!-- /build:ansi -->

Decisions behind the table:

- **The six hues keep their meaning.** Red, green, yellow, blue, purple (ANSI magenta) and cyan map to feedback and syntax roles. The six categorical `data.*` colors are chart series, so they are not used here.
- **Bright is not neon.** Flatcap has no separate bright tier. Blue uses the stronger step of the accent ramp. The other hues repeat their normal role, so `ESC[91m` and `ESC[31m` look the same. No value was invented to fill the gap.
- **Black and bright white follow luminance; white is ink.** Programs use black (0) and bright white (15) as block backgrounds and as text on colored blocks, so black stays dark and bright white stays light in both modes. In Slate, black is the quiet border tone: visible as a block on the canvas, but not meant for reading text on it. In Daylight, bright white is the raised white surface. ANSI white (7) is different: TUIs such as bottom (ratatui `Color::Gray`), htop and mc use it as their ordinary text, so it is `text.secondary` in both modes and reads on the canvas (8.4:1 in Slate, 7.1:1 in Daylight). It is no longer a light block color in Daylight.
- **Bright black is dimmed text, not black.** Shells such as PowerShell (PSReadLine) and zsh draw suggestions and comments with it, so it uses the muted text role.
- **Cursor** uses the interaction accent, not the focus ring. Focus and the text cursor are independent signals in Flatcap. Prefer the `bar` cursor: how the character under a block cursor is drawn with a custom cursor color has not been verified in Windows Terminal.

## Accessibility and limitations

Measured on the generated values, as text on the scheme background unless noted. The program output you see is a mix of these 16 colors and whatever true-color values your tools choose themselves.

<!-- build:contrast -->
| Pair | Slate | Daylight | Target | Result |
| :--- | ---: | ---: | ---: | :--- |
| `foreground` on `background` | 12.15:1 | 12.06:1 | 7:1 | met |
| Hues (red…cyan, normal and bright) on `background`, lowest | 7.91:1 | 5.66:1 | 5:1 | met |
| `brightBlack` (dimmed text) on `background` | 7.96:1 | 5.71:1 | 5:1 | met |
| `cursorColor` on `background` | 8.80:1 | 6.42:1 | 3:1 | met |
| `foreground` on `selectionBackground` | 5.64:1 | 9.45:1 | 4.5:1 | met |
| Hues and `brightBlack` on `selectionBackground`, lowest | 3.67:1 | 4.43:1 | 4.5:1 | not met: see the selection note below |
| `selectionBackground` vs `background` | 2.15:1 | 1.28:1 | none | informational |

Colors that fall short of 4.5:1 as text on `selectionBackground` (colors with equal values are grouped):

- Slate: `red`/`brightRed` 3.67:1; `green`/`brightGreen` 4.07:1; `yellow`/`brightYellow` 4.29:1; `blue` 4.08:1; `purple`/`brightPurple` 3.74:1; `cyan`/`brightCyan` 4.47:1; `white` 3.91:1; `brightBlack` 3.69:1.
- Daylight: `red`/`brightRed` 4.44:1; `purple`/`brightPurple` 4.43:1; `brightBlack` 4.48:1.

Text on ANSI background colors (`ESC[4Xm`), as ratio of the text color on that background:

| Background | Slate: `black` | Slate: `brightWhite` | Daylight: `black` | Daylight: `brightWhite` |
| :--- | ---: | ---: | ---: | ---: |
| `red` | 4.46:1 | 1.54:1 | 2.13:1 | 6.20:1 |
| `green` | 4.96:1 | 1.38:1 | 1.97:1 | 6.68:1 |
| `yellow` | 5.22:1 | 1.31:1 | 1.90:1 | 6.95:1 |
| `blue` | 4.97:1 | 1.38:1 | 1.88:1 | 7.01:1 |
| `purple` | 4.56:1 | 1.51:1 | 2.13:1 | 6.18:1 |
| `cyan` | 5.44:1 | 1.26:1 | 2.07:1 | 6.36:1 |
<!-- /build:contrast -->

- **Selection has no foreground.** Windows Terminal supports `selectionBackground` but not a selection foreground, so Flatcap's `selection.fg` cannot be applied. Selected text keeps its own color. Primary text stays readable on the selection in both modes, but some tinted colors fall short of 4.5:1 (listed above) and remain legible rather than comfortable. The selection fill is also subtle against the background, especially in Daylight. This follows the core roles and has not been changed.
- **Colored backgrounds take different text in each mode.** Slate's colors are light, so text on an ANSI background (`ESC[4Xm`) should be dark: `black` meets or approaches 4.5:1 on all six. Daylight's colors are dark, so it should be light: `brightWhite` clears 4.5:1 on all six. A program that hard-codes white-on-red for a dark terminal is low contrast in Slate, and black-on-red is low contrast in Daylight (see the last table above). Windows Terminal's `adjustIndistinguishableColors` may correct some of these cases; Flatcap does not set it and its effect here has not been verified. Test the tools you use daily (htop, mc, vim status lines).
- **Neutral blocks.** ANSI black in Slate and bright white in both modes are for filling blocks, not for reading on the canvas (bright white is `bg.raised` in Daylight: 1.1:1). Text drawn in `ESC[97m` (or bold white with `intenseTextStyle: "all"`, which brightens index 7 to 15) is therefore nearly invisible in Daylight. Windows Terminal can nudge such text with `adjustIndistinguishableColors`, which Flatcap does not set for you. If a tool you use hits this, `"intenseTextStyle": "bold"` avoids the brightening (see below).
- **White on dark blocks in Daylight.** Because white (7) is ink in Daylight, white text on a dark ANSI background (`ESC[37;4Xm`) is low contrast there (1.1 to 1.3:1 on the hues). Use bright white for text on colored blocks; programs that hard-code plain white on blue or red are the exposed case.
- **Selected rows with dark text on blue in Daylight.** Tools such as bottom draw the selected row as black text on the blue background. In Daylight black is ink and blue is dark, so that pair is low contrast (about 1.9:1). This follows from the role mapping and is a known limitation; see `adjustIndistinguishableColors` in Windows Terminal.
- **Acrylic and opacity change the colors you see.** `useAcrylic` and `opacity` below 100 blend the desktop into the background, so every contrast figure in this README no longer applies, most noticeably in Daylight, where the tint shifts the near-white canvas and washes out light fills. Flatcap is matte: keep `opacity` at 100 and `useAcrylic` false (Windows Terminal's defaults; the snippet does not change them), and always use those values for screenshots.
- **Intense text: `"intenseTextStyle": "all"`.** Windows Terminal's default is `bright`, which brightens indexed colors but does not bold, so bold text in the default color (headings, `man` pages) may show no emphasis. `all` bolds it and also maps old-style "bold black" (`ESC[1;30m`) to bright black, the readable dim tone, instead of leaving it dark on dark. Because Flatcap's bright colors mostly repeat the normal ones, brightening has no unwanted color shift. Use `bold` if you want weight only.
- **Dim (`ESC[2m`)** is rendered by Windows Terminal; its exact blend was not measured.
- **16 colors only.** Prompts and tools that emit their own true-color values (oh-my-posh, starship themes, `bat`, `delta`) ignore the scheme. Their colors are theirs; choose Flatcap-compatible themes there.
- **Tabs.** Window themes cannot add an indicator beyond fill, so the active tab is told apart by its color only.
- **Not verified in Windows Terminal itself.** The schemes were validated against the official JSON schema and their contrast was computed. A first check in a real Windows Terminal (bottom in Daylight) found ANSI white unreadable; that is fixed here. The rest of the 16 colors, bold, dim, inverse and the tools you use daily have not been checked in full yet.

## Compatibility

| Feature | Minimum Windows Terminal | Notes |
| :--- | :--- | :--- |
| Color schemes | any current version | Fragment schemes must define all 16 colors; they do. |
| JSON fragment extensions | 1.7 | Option A. |
| `intenseTextStyle` | 1.10 | `all`, `bold`, `bright`. |
| Font features (`calt`) | 1.11 | Optional. |
| Window themes (`themes`, `theme`) | 1.16 | JSON only; not installable from a fragment. |
| `colorScheme` and `theme` as `light`/`dark` pairs | 1.17 | Follow the Windows appearance. |
| `window.frame` and `window.unfocusedFrame` | 1.19 | Windows 11 only. |

Versions come from the official [color schemes](https://learn.microsoft.com/windows/terminal/customize-settings/color-schemes), [themes](https://learn.microsoft.com/windows/terminal/customize-settings/themes), [profile appearance](https://learn.microsoft.com/windows/terminal/customize-settings/profile-appearance) and [JSON fragment](https://learn.microsoft.com/windows/terminal/json-fragment-extensions) documentation and the [release notes](https://github.com/microsoft/terminal/releases). The pair syntax needs 1.17: on an older version use a single `colorScheme` name.

## How it is built

The JSON files and the tables in this README are generated; do not edit them by hand.

- `src/theme.json` holds the Flatcap 2.0 values. It is a copy of the core.
- `scripts/build.py` maps roles to scheme fields and window theme fields. The mapping and its intent live in the tables at the top of the script. It needs Python 3.10+ and nothing else.

```sh
python3 scripts/build.py              # regenerate the JSON files and the README tables
python3 scripts/build.py --check      # fail if they are out of date
python3 scripts/build.py --sync       # refresh src/theme.json from ../00-Flatcap, then rebuild
python3 scripts/build.py --contrast   # print the full contrast report, including the 16x16 matrix
python3 scripts/build.py --schema FILE  # also validate against the official schema (needs: pip install jsonschema)
```

The official schema is at <https://aka.ms/terminal-profiles-schema>; download it and pass its path to `--schema`. `--sync` expects the core checkout next to this repository (`../00-Flatcap`); pass a path to use another one.

Colors come from [Flatcap](https://github.com/cheycron/flat-cap-theme), the core of the system.

## License

MIT. Cascadia Code is not bundled and carries its own license (SIL OFL 1.1).

## Support

If Flatcap makes your terminal calmer, you can support its development.

<p align="center">
  <a href="https://www.buymeacoffee.com/cheycron">
    <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me a Coffee">
  </a>
</p>
