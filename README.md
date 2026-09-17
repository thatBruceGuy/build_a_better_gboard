# build_a_better_gboard

A personal fork of [FUTO Keyboard](https://github.com/futo-org/android-keyboard)
with a much smaller on-screen footprint.

Target: **595px / 170dp** of screen on a 1440px-wide, 3.5x-density phone,
against 845px for the Gboard layout this was measured from and 1034px for the
Samsung keyboard at *its smallest setting*. Roughly 30% less screen than Gboard.

Upstream's README is kept at [README-FUTO.md](README-FUTO.md).

## Where the numbers came from

Three keyboard screenshots from the same phone were measured pixel by pixel
with [`tools/measure_keyboard.py`](tools/measure_keyboard.py), not estimated.
All were 1440px wide, so they compare directly. The tool's full output for all
three is kept verbatim in
[`tools/reference-measurements.txt`](tools/reference-measurements.txt), which is
the baseline a re-measurement should be diffed against.

| | Samsung (smallest) | Gboard | FUTO (stock) |
|---|---|---|---|
| Chrome above keys | 180px / 51dp | 182px / 52dp | 294px / 84dp *(actions expanded)* |
| Letter keycap | 154px / 44.0dp | 100px / 28.6dp | 94px / 26.9dp |
| **Letter row pitch** | **176px / 50.3dp** | **131px / 37.4dp** | **123px / 35.1dp** |
| Row gap | 21px | 31px | 29px |
| Side padding | 24px | 17px | 15px |
| Bottom padding | 22px | 42px / 12dp | 35px / 10dp |
| **Total panel** | **1034px / 295dp** | **845px / 241dp** | **~821px / ~235dp** |

One caveat on that last column before anything else, because it is easy to
misread. It is not FUTO at its defaults. FUTO's default row height on this phone
works out to about 61dp:

```
getDefaultKeyboardHeight = max(min(205.6dp * 3.5, 0.46 * 3088), 0.618 * 1440)
                         = max(min(719.6, 1420), 890) = 890px
singularRowHeight        = (890 - 35) / 4 = 214px = 61dp
```

The measured pitch was 35.1dp, so a height multiplier of roughly 0.58 was
already set in settings when the screenshot was taken. Much of the easy headroom
had been spent before this fork started, and the fork's gain over a *fresh*
FUTO install is correspondingly larger than the 35.1dp-to-30dp the table
suggests. Since this fork has its own applicationId it installs with a fresh
datastore, so it starts at a multiplier of 1.0 and the 30dp pitch is what a new
install actually gets.

Two further results are worth stating plainly, because they are the opposite of
what the screenshots suggest:

**FUTO's key rows were already tighter than Gboard's** — 35.1dp pitch against
37.4dp, 26.9dp keycaps against 28.6dp. The keys were never the problem.

**FUTO's action bar doubles in height when the actions are expanded.**
`calculateTotalActionBarHeightPx()` returned `2 x 40dp` in that state, pushing
the whole keyboard down by 140px. Collapsed, FUTO's chrome was 40dp against
Gboard's 52dp. Like for like, stock FUTO was already 42px *shorter* than
Gboard; the apparent bloat was that one expanded row.

The density (3.5x, 411dp wide) was derived from the screenshots and confirmed
against the source three ways: `ActionBarHeight = 40.dp` against a measured
140px strip, `calculateGap()` giving 4.11dp against a measured 15px key gap, and
`verticalGap = gap * 2` against a measured 29px row gap.

## What changed

| | Stock FUTO | Here |
|---|---|---|
| Row pitch | 123px | **105px** (30dp) |
| Keycap height | 94px | **91px** |
| Row gap | 29px | **14px** |
| Chrome, actions expanded | 280px | **140px** |
| Bottom padding | 35px | **21px** |
| **Total** | ~821px | **~595px** |

1. **The expanded actions row is an overlay.** It is drawn over the top key row
   instead of stacking above the action bar, so expanding costs no height.
2. **Row pitch cut to 30dp.** The catch is `config_min_keyboard_height`:
   `ResourceUtils` reads a *negative* fraction as a fraction of screen **width**,
   so the stock `-61.8%p` resolved to 890px on a 1440px phone and silently
   overrode `config_default_keyboard_height` entirely. Lowering the default
   alone does nothing.
3. **`VerticalGapMultiplier` 2.0 to 1.0.** At 2.0 a 30dp pitch would leave only
   ~22dp of visible keycap. At 1.0 the keycaps stay near 26dp and the reduction
   comes out of dead space between rows. Hit testing uses key bounds *including*
   the gap, so touch targets follow the pitch, not the painted keycap.
4. **Number row height ratio 0.8 to 0.85.** It stays off by default — the
   superscript digit hints are what let FUTO beat Gboard on total height.
5. **A "Compact Slate" theme** matching the reference Gboard layout: a
   `#5C5754` to `#1B1112` vertical gradient with translucent white keycaps
   (0.19 alpha) and a `#B45736` enter key.

Portrait only. `values-land` keeps its own heights.

Where the 595px comes from, so a later change can be re-derived rather than
guessed at:

```
getDefaultKeyboardHeight = max(min(126dp * 3.5, 0.46 * 3088), 0.20 * 1440)
                         = max(min(441, 1420), 288) = 441px
singularRowHeight        = (441 - 21) / 4 = 105px = 30dp   (at multiplier 1.0)
keycap height            = 105 - 14 (vertical gap) = 91px
total, no number row     = 4 * 105 + 21 + 140 (bar) + 14 (top pad) = 595px
total, number row on     = 4.5 * 105 + 21 + 140 + 14 = 648px
```

Note that `config_min_keyboard_height` at −20%p resolves to 288px here, still
below the 441px the default gives. Raising the default without checking that
minimum is how the stock values ended up with a dead `config_default_keyboard_height`.

## Verifying a change

The point of the measurement tool is that layout changes get checked against
numbers rather than impressions:

```bash
pip install pillow numpy
# Screenshot the keyboard, cropped so the image bottom is the screen bottom.
python3 tools/measure_keyboard.py shot.png --density 3.5
```

Expect a row pitch of 105px, keycaps of 91px, chrome of 140px and a total of
about 595px. Then screenshot again with the actions expanded: the total should
be unchanged, which is the test for change 1. The tool warns if the screenshot
is cropped into the keyboard, which makes the total meaningless.

[`tools/reference-measurements.txt`](tools/reference-measurements.txt) holds the
same tool's output for the three reference keyboards, in the same format, so a
new run can be compared against it line for line.

A toolbar or suggestion strip of icons can look like a key row to the detector.
The `keys` column tells them apart — letter rows have 9 or 10 — and
`--first-key-row N` counts leading strips as chrome.

## Building

```bash
git clone --recurse-submodules https://github.com/thatBruceGuy/build_a_better_gboard
cd build_a_better_gboard
./gradlew assembleUnstableDebug
```

`--recurse-submodules` is not optional: seven submodules carry the layouts,
dictionaries, translations and native libs. Most are hosted on
`gitlab.futo.org`, one on Hugging Face, so a GitHub-only clone will not build.
An Android SDK and NDK are needed for the native code.

The applicationId is `org.futo.inputmethod.latin.compact`, so this installs
alongside stock FUTO rather than replacing it. The Kotlin/Java namespace is
deliberately left as `org.futo.inputmethod.latin` to keep rebases against
upstream manageable.

## Two things that will waste your time

Both were hit while writing this fork, so they are recorded rather than
rediscovered.

**`keyboardFade0` and `keyboardFade1` are dead parameters.**
`extendedDarkColorScheme` and its light counterpart accept them
(`ColorScheme.kt` lines 182-183 and 272-273) but never use them — they are not
fields on `ExtraColors` and nothing reads them. Fourteen existing presets set
them and none of them have any effect. The real mechanism for a panel gradient
is `keyboardBackgroundGradient: Brush?`, which is a genuine `ExtraColors` field.
`CompactSlate` uses that.

**The number row toggle needed no code.** `Default/qwerty.yaml` sets no
`numberRowMode`, so it already resolves to `UserConfigurable` and the setting is
reachable from preferences. Only `NumberRowHeight` needed changing.

## Known risks

- **30dp pitch is past a comfortable default**, chosen deliberately. Type a
  paragraph of ordinary prose and compare the mistype rate against stock FUTO.
  If it is meaningfully worse, `config_default_keyboard_height` at 140dp gives a
  32dp pitch, and that is the only change needed.
- **The overlay covers the top key row while open.** It is opaque and consumes
  its own touches, so presses hit an action rather than falling through, but the
  row underneath is unreachable until the actions are collapsed.
- **None of this has been run on a device yet.** It was written against the
  source and checked by reading the diff; it has not been compiled or installed,
  because the machine it was written on had no Android SDK or NDK. Treat every
  number above as a prediction until `measure_keyboard.py` has been pointed at a
  real screenshot.

## Upstream

This repo is rooted at a single import commit (`4874ce6`) whose tree is
byte-for-byte upstream `a0b84ef`, not at the full upstream history. Upstream is
43,613 commits reaching back to AOSP LatinIME in 2009 and about 555MB, which
does not push in one pack. Nothing is lost — to diff or rebase against real
upstream history:

```bash
git remote add upstream https://github.com/futo-org/android-keyboard
git fetch upstream
git diff a0b84ef HEAD
```

The fork's own changes are `git diff 4874ce6 HEAD`.

GitHub's `futo-org/android-keyboard` is a read-only mirror of
`gitlab.futo.org/keyboard/latinime`, so changes here cannot be sent upstream
through GitHub in any case.

Note also that upstream asks people not to submit AI-generated pull requests
(see [README-FUTO.md](README-FUTO.md)), and these commits were written with
Claude. This fork is a personal build and is not intended for upstreaming.

FUTO Keyboard's own license terms apply; see [LICENSE.md](LICENSE.md).
