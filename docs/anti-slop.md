# The anti-slop approach

## Why AI interfaces all look the same

An LLM asked to "build a landing page" returns the median of its training data, which is years of Tailwind tutorials and template marketplaces. The median has a look: an indigo-to-purple gradient (Tailwind's `indigo-500` is the default a tutorial reaches for), an oversized centered headline, three equal rounded cards, an all-caps eyebrow above every section, a fake product screenshot in the hero, and body copy that "seamlessly elevates your workflow."

None of these are bugs individually. The problem is that they are defaults, chosen by no one, and they converge. The fix is not to ban words one at a time. It is to make deliberate choices up front and write them down, so every later decision has something specific to answer to.

That is what picasso is: a way to commit to one design system, record it as durable artifacts, and hold the work to it.

## The three moves

### 1. Decide before you build

The `taste` skill starts every piece of UI with a one-line Design Read: "Reading this as a `<page kind>` for `<audience>`, with a `<vibe>` language, leaning `<system or aesthetic>`." From that read it infers three dials rather than interrogating the user:

- **DESIGN_VARIANCE** (1 to 10): symmetry versus surprise.
- **MOTION_INTENSITY** (1 to 10): static versus cinematic.
- **VISUAL_DENSITY** (1 to 10): airy versus dense.

The dials are recorded in `design.md` and gate the downstream choices. A minimalist product lands near 5/3/2; a public-sector, trust-first site near 3/2/5. Committing to a point in that space is what prevents the sampler-of-effects look.

### 2. Lock consistency

A design reads as deliberate when a few things are decided once and never wander:

- one accent color, page-wide
- one corner-radius scale
- one theme (no section quietly inverts light and dark)
- one copy register
- one label per call-to-action intent

The hero gets its own discipline: it fits the viewport, at most two headline lines, subtext under twenty words, at most four text elements. Restraint here is most of the battle.

### 3. Make the tells visible

Some slop is mechanical and can be detected. picasso ships a linter (see the [reference](reference.md) for the full rule list) that flags the highest-signal tells: indigo/purple gradients, pure black, raw hex where a token should be, fabricated metrics, eyebrow overuse, image grids that overflow, and duplicate calls to action. It runs as a warn-only hook while you edit, and on demand through `/picasso:review`. A flag is a prompt to reconsider, not a wall.

## The specific tells it targets

Grouped roughly by where they hide:

- **Color and effects:** indigo/purple and blue/purple gradients, neon glows, gradient text on large headings, pure `#000000`, oversaturated accents.
- **Typography:** reflexive `Inter` or a reflexive serif chosen to signal "premium," oversized screaming headlines, a random serif word inside a sans headline.
- **Layout:** three equal rounded cards as the only feature pattern, a centered hero over a dark mesh gradient, the same zigzag section repeated, bento grids with filler cells.
- **Micro-labels:** an eyebrow above every section, section-number labels like `01 / FEATURE`, middle-dot separators everywhere, version stamps and "scroll to explore" cues.
- **Fake content:** invented dashboards and terminals in the hero, fabricated metrics like "+47% conversion" or "trusted by 50,000 teams," placeholder logo walls, generic testimonials.

## The deepest tell is structure, not vocabulary

The `unslop-copy` skill works in three passes, and the order matters. Removing clichés barely moves an AI-detection score; what gives machine-written prose away is its shape.

1. **Mechanics.** No em-dashes, one quote style, sentence-case headings, no "In summary" restatement, no chatbot debris.
2. **Vocabulary and rhetoric.** Cut inflated significance, promotional tone, negative parallelism ("not just X but Y"), the reflexive rule of three, and the dated AI vocabulary (delve, tapestry, leverage, robust). Watch for "clean slop," the second-order uniform that survives a first cleanup: an aphoristic one-liner closing every paragraph, uniform maximum confidence.
3. **Structure and epistemics.** Do not state the moral. Break the claim-support-takeaway symmetry. Use real specifics rather than invented ones. Leave some endings open, and leave slack. Never invent numbers or facts for liveliness. The outline test is the giveaway: read the first sentence of each paragraph; if they form a clean summary on their own, the structure is machine-shaped and needs reworking.

## What picasso deliberately does not do

- It does not clone reference sites. It extracts principles and labels borrowed inspiration.
- It does not recreate an official design system by hand. If your brief matches Material, Fluent, Carbon, Polaris, Primer, GOV.UK, or USWDS, use that system rather than reimplementing its tokens.
- The demo screens are compositions for feedback, not a mirror of real features. They exist so you can see the components arranged on a page, not to stay in sync with the app.
- The linter never blocks. Taste is a judgment; the tools inform it, they do not overrule it.
