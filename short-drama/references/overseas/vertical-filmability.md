---
layer: modes
control: mixed_gate
authority_id: short-drama.overseas-vertical-filmability
canonical_path: references/overseas/vertical-filmability.md
read_when: mode is overseas before /分集, /自检, scene polish, and production feasibility review
---

# Vertical Filmability Anti-Patterns

Purpose: catch writing that fails because it cannot be read, shot, or understood in 9:16 vertical video.

9:16 physics and hook-window rationale live in `platform-knowledge.md`. This file only covers scene-level craft and filmability failures.

## AP-V2: Wide Establishing Shots

**Pattern**: Opening with a landscape, building exterior, or skyline to "set the scene."

```text
WRONG:
FADE IN:
EXT. BLACKWELL UNIVERSITY - DAWN
Gothic spires rise above morning mist. Students cross the quad in twos and threes.
The bell tower strikes seven. Autumn leaves scatter across cobblestone paths.

RIGHT:
FADE IN:
INSERT - GARGOYLE: stone teeth bared, morning frost on its lip. Below it, a hand pushes open an iron gate.

(SFX: gate hinge -- a slow, reluctant groan)

Elara's breath fogs in the cold. She doesn't look up at the gargoyle. It looks down at her.
```

**Why it fails**: Wide shots are unreadable at 9:16 resolution on a phone screen. The first 3 seconds must be a visual anchor (see `platform-knowledge.md` section 2: 50-60% of viewer dropoff happens by 3s), a specific concrete image, not a panorama. Establishing mood through environment description wastes the hook window.

**Rule**: Replace every wide establishing shot with one INSERT detail that implies the whole environment. A gargoyle implies Gothic campus. A signet ring implies mafia dynasty. A cracked mirror implies decay.

## AP-V3: Unfilmable Choreography

**Pattern**: Writing action sequences that require multiple simultaneous actors, complex blocking, or physical stunts.

```text
WRONG:
Julian kicks the table into Marco's legs while spinning to grab the gun
from the third man's holster. Elara ducks behind the bar as bullets shatter
the mirror. Julian fires twice -- one man drops, the other crashes through
the window. Glass everywhere.

RIGHT:
Julian's hand closes around the gun on the table. One motion.

(SFX: a single gunshot -- then ringing silence)

INSERT - SHATTERED GLASS: a whiskey tumbler, not a window. The crack runs through Julian's reflection.

Marco stares. Doesn't move. The third man is already gone -- running footsteps fade down the corridor.

Elara watches from behind the bar. Julian's hand is steady. His eyes are not.
```

**Why it fails**: 9:16 vertical video uses single-subject framing. The camera follows one person at a time. Simultaneous multi-character blocking is unfilmable in vertical. Complex fight choreography requires wide shots and careful spatial blocking, both impossible at 9:16.

**Rule**: Violence should usually be shown through **consequence and reaction**, not choreography. One decisive action + one reaction shot + one INSERT of aftermath is the default. Escalate to hard gate only when the action is unreadable, unfilmable in 9:16, or violates `hard-rules.md` violence calibration.

## AP-V4: Interior Monologue as Scene Driver

**Pattern**: Extended internal monologue via VO drives the scene instead of visible action.

```text
WRONG:
ELARA (V.O.)
I knew I should leave. Every instinct screamed to run. But something
about the way he looked at me -- not with hunger, not with anger, but
with recognition, like he'd been waiting for me to walk through that
door -- made my feet root to the floor. I'd been invisible my whole
life. And now someone was finally seeing me. The worst possible someone.

RIGHT:
Elara's hand is on the door handle. She pulls it down.

Stops.

Julian hasn't moved. Hasn't spoken. He's watching her the way a man watches
something he's already decided to keep.

Her hand releases the door handle.

ELARA
(to herself, barely audible)
Don't.

She sits back down.
```

**Why it fails**: Interior monologue is the novel's tool, not the screenplay's. In vertical video, the audience watches faces and actions; they do not read minds. Extended VO monologue turns visual media into an audiobook with pictures.

**Boundary**: VO itself is platform-standard (see `platform-knowledge.md` section 5), but its function is brief self-introduction or emotional tag, not narrative exposition.

## AP-V5: Dialogue-Free Establishing Sequences Over 30s

**Pattern**: Extended wordless sequences meant to build atmosphere before any character interaction.

**Why it fails**: Vertical drama audiences decide to stay or leave within 3-15 seconds. A 30+ second wordless atmospheric sequence is a feature-film luxury. In roughly 90-second episodes (see `platform-knowledge.md` section 1), 30s wordless equals one third of runtime and is indefensible.

**Rule**: Maximum wordless/dialogue-free stretch defaults to 15s, one Hook or Establish sub-segment. After 15s, either dialogue, VO with a valid platform function, or a new character should enter the frame. Escalate to hard gate only when the silence consumes the hook window or blocks viewer comprehension.

## AP-V6: Talking Heads -- Dialogue Without Physical Action

**Pattern**: Two characters talking with no physical action, prop interaction, or spatial movement.

```text
WRONG:
JULIAN
I need the research files.

ELARA
They're not ready.

JULIAN
When will they be ready?

ELARA
When I say they are.

JULIAN
That's not how this works.

ELARA
Then change how it works.

RIGHT:
Julian picks up the specimen jar from Elara's desk. Holds it to the light.

JULIAN
I need the research files.

ELARA
They're not ready.

She takes the jar from his hand. Places it back. Exactly where it was. To the millimeter.

JULIAN
When will they be ready?

ELARA
(adjusting the jar's label to face him)
When I say they are.

Julian's fingers tap the desk. Once. Twice. He stops.

JULIAN
That's not how this works.

ELARA
(doesn't look up)
Then change how it works.
```

**Why it fails**: 9:16 video without physical action can become radio with a static image. Dialogue scenes should regularly include hands doing something, objects being manipulated, or spatial relationships shifting. This is a strong craft diagnostic; escalate to hard gate only when a scene becomes visually static enough to fail phone-screen readability or retention.
