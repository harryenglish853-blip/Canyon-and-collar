"""
Canyon & Collar — single source of truth for the cinematic asset package.

Everything downstream (generation prompts, the web asset manifest, and the
procedural proxy plates) is built from the data in this file, so the style,
continuity and journey timeline can never drift between them.

    python3 tools/build.py
"""

BRAND = {
    "name": "CANYON & COLLAR",
    "tagline": "LUXURY STAYS. GROUNDED IN NATURE.",
}

# ---------------------------------------------------------------------------
# The film. One continuous piece of footage plays behind the entire scroll
# journey; the chapters below supply the timing and the typography over it.
# ---------------------------------------------------------------------------
FILM = {
    "src": "assets/video/canyon_collar_film.mp4",
    "width": 1280,
    "height": 720,
    "duration": 10.06,
    "fps": 24,
    "hasAudio": True,
    "note": "Supplied footage. Single keyframe, so it is played and looped rather "
            "than scrubbed — seeking this encode frame by frame would stutter.",
}

# ---------------------------------------------------------------------------
# Palette. Locked. Every prompt and every proxy plate pulls from here.
# ---------------------------------------------------------------------------
PALETTE = {
    "sandstone":     "#D8C3A5",
    "warm_beige":    "#E4D5C3",
    "desert_clay":   "#B4704F",
    "sage":          "#8A9A7B",
    "charcoal":      "#33312E",
    "deep_olive":    "#4A4F3C",
    "leather_brown": "#6B4A32",
    "cream":         "#F3EBDF",
    "muted_rust":    "#9C5B3C",
    "soft_black":    "#1A1816",
    "sunset_amber":  "#E0A04A",
}

# Lighting states. Each proxy plate and each prompt references one of these so
# the scroll journey reads as one continuous day.
LIGHT = {
    "afternoon": {
        "label": "late afternoon, warm and open",
        "sky":   ["#EBD9BC", "#DCC49C", "#C99C6E"],
        "land":  ["#B98C61", "#8E6746", "#5E462F"],
        "key":   "#F0C489",
        "haze":  "#F3E3C6",
        "prompt": "late afternoon desert light, warm but not hot, long soft shadows, "
                  "gentle atmospheric haze, sun still above the ridgeline",
    },
    "golden": {
        "label": "golden hour, low sun",
        "sky":   ["#F6DDA8", "#E8B071", "#C0714A"],
        "land":  ["#A9703F", "#7E4F31", "#4A2F20"],
        "key":   "#FFD79A",
        "haze":  "#F7DFB4",
        "prompt": "golden hour, low raking sun just above the canyon rim, long shadows, "
                  "warm rim light on fur, natural subtle lens flare, floating dust in the beam",
    },
    "interior_day": {
        "label": "interior, filtered daylight",
        "sky":   ["#EFE2CC", "#E0CDB0", "#C4A986"],
        "land":  ["#A08663", "#75604A", "#463A2D"],
        "key":   "#FFE6BC",
        "haze":  "#F1E2C9",
        "prompt": "filtered daylight through a large window, soft warm bounce off plaster, "
                  "quiet interior, dust suspended in a shaft of sun",
    },
    "interior_lamp": {
        "label": "interior, warm lamp light",
        "sky":   ["#7A6248", "#5A4634", "#392D22"],
        "land":  ["#4A3A2B", "#332920", "#1E1812"],
        "key":   "#F0B76E",
        "haze":  "#8A6A48",
        "prompt": "warm bedside lamp light, pools of low amber light, deep soft shadows, "
                  "no overhead lighting, calm and residential",
    },
    "dusk": {
        "label": "evening, deep blue sky against warm windows",
        "sky":   ["#3E4E64", "#2B3purple", "#1B2231"],
        "land":  ["#2C2A26", "#211F1C", "#141311"],
        "key":   "#E8A85C",
        "haze":  "#54617A",
        "prompt": "deep blue evening sky, warm interior windows glowing, low exterior path "
                  "lighting, quiet and safe, no harsh contrast",
    },
    "morning": {
        "label": "early morning, clean cool-warm light",
        "sky":   ["#F2E7D4", "#E3D3B6", "#C9B591"],
        "land":  ["#A88F6C", "#7C6850", "#4C4032"],
        "key":   "#FFF0D2",
        "haze":  "#F5EBD8",
        "prompt": "early morning desert light, clean and clear, soft warm sun low through "
                  "the window, cool shadow side, fresh and quiet",
    },
    "macro": {
        "label": "macro, controlled warm light",
        "sky":   ["#C7AE8B", "#9C8261", "#6B563E"],
        "land":  ["#584533", "#3D2F23", "#241C15"],
        "key":   "#FFD79A",
        "haze":  "#B59straight",
        "prompt": "single warm directional light with soft fill, controlled specular "
                  "highlights, everything else falling into shadow",
    },
}
# guard against typos above being silently used
LIGHT["dusk"]["sky"][1] = "#2B3448"
LIGHT["macro"]["haze"] = "#B5946C"

# ---------------------------------------------------------------------------
# Continuity locks — pasted verbatim into every single prompt.
# ---------------------------------------------------------------------------
CONTINUITY = (
    "SAME PROPERTY THROUGHOUT: a single-storey desert-modern retreat of warm sandstone "
    "block, weathered vertical cedar slats, hand-troweled sand-coloured plaster, deep "
    "shaded overhangs, and tall bronze-framed glass. Native planting only — sage, "
    "juniper, desert grasses, mesquite, agave, decomposed-granite paths edged in stone. "
    "SAME HERO DOG: one calm, elegant Golden Retriever with a mid-gold coat, slightly "
    "darker ears, a quiet expressive face, wearing an aged brown leather collar with "
    "matte brass hardware and a small brass tag. SAME STAFF WARDROBE: soft olive or "
    "charcoal overshirt, cream or khaki trousers, dark brown leather belt, no logos, no "
    "scrubs. SAME PROPS: aged brown leather leash, matte brass hardware, cream stoneware "
    "bowls with a thin charcoal rim, oatmeal linen bedding, natural jute and wool textures."
)

NEGATIVE = (
    "clinical white veterinary interior, kennel cages, wire crates, rows of pens, chain "
    "link, chaotic pack of dogs, bright plastic toys, neon colours, artificial turf, "
    "pet-store signage, cartoon paw prints, childish graphics, gold marble, glossy luxury "
    "cliche, oversaturated HDR, heavy vignette, over-sharpened, plastic fur, waxy skin, "
    "deformed paws, extra limbs, distorted faces, warped architecture, text artifacts, "
    "watermark, logo overlay, stock-photo smiling, forced grin on dog, fisheye distortion, "
    "drone hyperlapse, teal-and-orange grade, lens dirt overlay, motion smear"
)

TECH_IMAGE = (
    "photorealistic editorial photography, medium-format digital capture, natural colour "
    "science, fine natural grain, true fur and material texture, no digital sharpening halo, "
    "highlight rolloff retained, shadows open and warm"
)

TECH_VIDEO = (
    "24fps cinematic motion, natural motion blur, physically grounded camera, no speed ramps "
    "unless specified, no whip pans, no drone, subtle film grain, stable horizon"
)

# ---------------------------------------------------------------------------
# The journey. scroll = (start, end) as fractions of the full page scroll.
# mode drives proxy composition: EXT | INT | MACRO
# ---------------------------------------------------------------------------
ASSETS = [
    dict(
        id="01", slug="canyon_collar_arrival", outputs=["image", "video"],
        title="OPENING HERO / ARRIVAL", chapter="ARRIVAL",
        scroll=(0.00, 0.08), duration="5-8s", lens="35mm", ratio="2.39:1",
        mode="EXT", light="golden", negative_space="upper left third and sky band",
        overlay=["CANYON & COLLAR", "LUXURY STAYS. GROUNDED IN NATURE."],
        subject="The hero Golden Retriever, seated square and calm on a decomposed-granite "
                "path at the entrance, head turned three-quarters toward the open doorway.",
        scene="Wide establishing frame of the Canyon & Collar entrance. Low sandstone block "
              "walls step back into the slope. A deep timber-slatted overhang shades a "
              "bronze-framed glass entry that glows warm from within. Sage and desert grasses "
              "break the hard geometry along the path. Red canyon walls rise soft and hazy "
              "behind the roofline. The dog is small in frame, lower right, dwarfed by the "
              "architecture and the landscape — the property is the subject, the dog is the "
              "reason you are looking.",
        camera="35mm. Camera parked low, at the dog's eye height, so the building rises above "
               "the lens. Deep focus front to back, f/5.6 feel. Horizon dead level.",
        motion="Very slow dolly-in on the axis of the path, roughly 15cm per second. Nothing "
               "else moves except grass in a light breeze and one slow tail shift. The building "
               "grows almost imperceptibly. Hold the final frame for a full second before cut.",
        audio="desert breeze through grasses, distant canyon wren, a single soft collar-tag "
              "chime, very low sustained string pad entering at 2s",
        transition="Opens cold from black. Out on a soft sunlight bloom that hands off to 02.",
    ),
    dict(
        id="02", slug="concierge_welcome", outputs=["video"],
        title="THE WELCOME", chapter="WELCOME",
        scroll=(0.08, 0.15), duration="5-7s", lens="50mm", ratio="2.39:1",
        mode="EXT", light="afternoon", negative_space="upper right",
        overlay=["A BETTER KIND OF STAY."],
        subject="The hero dog between its owner and a Canyon & Collar concierge who has come "
                "down onto one knee.",
        scene="Just inside the entrance court, on warm stone paving under the timber overhang. "
              "The owner stands half out of frame, holding the leather leash. The concierge — "
              "olive overshirt, khaki trousers — lowers to the dog's level, body turned "
              "slightly away rather than square-on, hand offered low and open, not reaching "
              "over the head. The dog leans in to sniff the offered hand, ears relaxed, mouth "
              "soft. No hugging, no grabbing, no crouching over the animal. Restrained, "
              "professional, obviously practised.",
        camera="50mm, f/2.0. Shallow depth of field — the offered hand and the dog's face sit "
               "in the plane of focus, the owner and the architecture fall soft.",
        motion="Slow lateral tracking move left to right, arcing gently around the greeting, "
               "combined with a subtle rack focus from the owner's hand on the leash to the "
               "dog's eyes as it commits to the greeting.",
        audio="quiet footsteps on stone, leash hardware, one soft exhale from the dog, warm "
              "room tone, piano enters on a single low note",
        transition="In from 01's sunlight bloom. Out by pushing toward the leash for 03.",
    ),
    dict(
        id="03", slug="leash_handoff", outputs=["video"],
        title="LEASH HANDOFF TRANSITION", chapter="WELCOME",
        scroll=(0.15, 0.22), duration="4-6s", lens="100mm macro", ratio="2.39:1",
        mode="MACRO", light="macro", negative_space="left third",
        overlay=[],
        subject="Two hands and one aged brown leather leash.",
        scene="Extreme close work. The owner's hand holds the worn leather leash, thumb "
              "creased into the strap. The concierge's hand enters frame and takes it — fingers "
              "closing below, not snatching — and the owner's hand releases and leaves frame. "
              "Camera continues past the hands to the brass snap hook and the small engraved "
              "tag. Every material flaw is visible and wanted: leather pores, a darkened patch "
              "where it has been held for years, micro-scratches across brushed brass, the "
              "faint warm bloom of low sun across the metal.",
        camera="100mm macro, f/2.8, razor-thin plane of focus. Frame is mostly negative fall-off "
               "— one lit object, everything else dark and soft.",
        motion="Continuous slow macro push along the leash toward the buckle. As the buckle "
               "fills frame, defocus it entirely into a warm brass bloom — that bloom is the "
               "match cut into the interior of 04. No cutaways, one unbroken move.",
        audio="leather creak, the exact click of a brass snap hook, breath, everything else "
              "dropping away to near-silence for the match cut",
        transition="Out on a defocused brass bloom that becomes the warm interior light of 04.",
    ),
    dict(
        id="04", slug="private_suite", outputs=["image", "video"],
        title="THE SUITE", chapter="THE SUITE",
        scroll=(0.22, 0.32), duration="6-8s", lens="35mm", ratio="2.39:1",
        mode="INT", light="interior_day", negative_space="left wall plane",
        overlay=["PRIVATE SUITES.", "ROOM TO REST."],
        subject="The hero dog entering its own private suite for the first time.",
        scene="A boutique hotel room built for a dog. Hand-troweled plaster walls in warm sand. "
              "A low platform bed in pale oak with a thick oatmeal linen-covered mattress, "
              "obviously washable, obviously soft. A tall window from knee height to ceiling "
              "framing sage and canyon rock, sun laid in a clean warm rectangle across honed "
              "stone floor. Two cream stoneware bowls set into a recessed oak ledge. A small "
              "open storage nook holding a folded blanket and a toy. A single small brass "
              "plate on the door jamb, blank enough to brand later. Beyond a second glass door, "
              "a private walled patio with one shade sail and a juniper. No bars, no mesh, no "
              "hardware that reads as containment. The dog steps in, nose down, reading the "
              "room, tail level and loose.",
        camera="35mm, f/2.8, lens at the dog's shoulder height so the room reads at dog scale.",
        motion="Slow dolly through the doorway following just behind and beside the dog, the "
               "door frame wiping past the foreground at the start. Settle as the dog reaches "
               "the light rectangle on the floor and turns to look back at camera.",
        audio="nails on stone, door easing on its hinge, the hollow quiet of a well-built room, "
              "faint breeze on the patio",
        transition="In from 03's brass bloom. Out on a cut to macro for 05.",
    ),
    dict(
        id="05", slug="personal_belongings", outputs=["video"],
        title="PERSONAL BELONGINGS", chapter="THE SUITE",
        scroll=(0.32, 0.37), duration="4-6s", lens="85mm", ratio="2.39:1",
        mode="MACRO", light="interior_day", negative_space="upper right",
        overlay=[],
        subject="A staff member's hands placing this dog's own things into the suite.",
        scene="A short series of unhurried close-ups on the oak ledge and the bed. A worn "
              "plaid blanket from home, folded once and set down with two hands and a smoothing "
              "pass. A soft toy with the fur licked flat on one side, placed beside the bed, not "
              "on it. A labelled food container set square. The leather collar's brass name tag "
              "lifted between two fingers and turned to the light. Nothing staged perfectly — "
              "the blanket keeps its creases, the toy is genuinely used. The point is that these "
              "objects came from a house, not a shop.",
        camera="85mm, f/2.0, shallow. Consistent left-to-right slider geography across all "
               "sub-shots so they cut as one continuous space.",
        motion="Slow slider moves, one per object, each ending in a brief rest. Hands enter and "
               "leave frame; faces never appear. Optional single rack focus from the tag to the "
               "bed behind it.",
        audio="fabric on fabric, a tag ticking against stoneware, careful quiet handling, no music "
              "swell — restraint",
        transition="Out on the blanket settling, cut to exterior light for 06.",
    ),
    dict(
        id="06", slug="nature_walk", outputs=["image", "video"],
        title="NATURE WALK", chapter="NATURE",
        scroll=(0.37, 0.47), duration="6-10s", lens="35mm", ratio="2.39:1",
        mode="EXT", light="afternoon", negative_space="upper band / sky",
        overlay=["GROUNDED IN NATURE."],
        subject="A concierge walking the hero dog on a maintained desert trail.",
        scene="A wide decomposed-granite trail curving along the base of a canyon wall on the "
              "property. Sage, bunched desert grasses, mesquite throwing lace shadows, low stone "
              "edging that says this land is cared for, not wild. Soft mountain silhouettes "
              "layered back into haze. The leash hangs in a relaxed J — never taut. The dog "
              "walks slightly ahead, stops to read a grass clump, moves on. The concierge waits "
              "for it without pulling. Comfortable warmth, not punishing heat: everything green "
              "that should be green.",
        camera="35mm, f/4. Tracking from the side at the dog's shoulder height, the trail edge "
               "running through the bottom of frame.",
        motion="Steady lateral tracking shot matched exactly to walking pace, so the dog holds "
               "its position in frame and the landscape slides behind. One natural beat where "
               "both stop, the camera drifts a half-step past, and the dog looks out at the "
               "canyon.",
        audio="granite underfoot, collar hardware in rhythm, breeze, two distant birds, acoustic "
              "guitar figure entering under the stop-and-look beat",
        transition="Out on the dog turning off-trail, cut wide to 07.",
    ),
    dict(
        id="07", slug="outdoor_exploration", outputs=["video"],
        title="OFF-LEASH EXPLORATION", chapter="PLAY",
        scroll=(0.47, 0.54), duration="5-8s", lens="50mm", ratio="2.39:1",
        mode="EXT", light="afternoon", negative_space="right third",
        overlay=[],
        subject="The hero dog off-leash in a secure, spacious play yard with two compatible "
                "companions.",
        scene="A large enclosed natural yard — not a dog park. Sandstone boundary walls, a "
                "broad shade structure in timber and canvas, natural ground cover and coarse "
                "grass, boulders placed to be climbed, a stone water station at the edge. Three "
                "dogs only: the hero Golden, an Australian Shepherd, and a French Bulldog, each "
                "doing its own thing — one trotting a wide arc, one nose-down under a shrub, one "
                "flopped in shade. A concierge stands calmly at frame edge, watching, hands "
                "loose. Space everywhere. Nothing frantic.",
        camera="50mm, f/2.8. Tracking at mid-height, then dropping low for the run-past.",
        motion="Slow tracking move that lets the hero dog run into and through frame; one "
               "restrained slow-motion beat (60fps conformed, no more) on the moment its front "
               "paws leave the ground, then back to real time immediately. No repeated ramping.",
        audio="paws on grit, a short play-bow huff, wind, no barking chaos, percussion picking "
              "up lightly and settling again",
        transition="Out as the dog heads for the water station — direct motivation into 08.",
    ),
    dict(
        id="08", slug="fresh_water", outputs=["video"],
        title="WATER / REFRESH", chapter="CARE",
        scroll=(0.54, 0.58), duration="4-6s", lens="100mm macro", ratio="2.39:1",
        mode="MACRO", light="afternoon", negative_space="upper left",
        overlay=[],
        subject="Water, a stoneware bowl, and a wet nose.",
        scene="Macro on the cream stoneware bowl at the shaded water station. Sun catches the "
              "meniscus and throws a caustic ring onto the stone below. The dog's muzzle enters "
              "frame, nose wet and textured, tongue curling water up in a clean scoop. Droplets "
              "break the surface tension and ride off the chin. The sky and the canyon rim sit "
              "reflected and inverted in the water until the tongue destroys them. Cut to a "
              "staff hand lifting the bowl, tipping it out, and refilling it with clean water — "
              "a small act nobody was asked to film.",
        camera="100mm macro, f/2.8, focus plane on the waterline. Camera at bowl height, on the "
               "ground.",
        motion="Slow motion at 120fps conformed to 24, but only on the drink itself; the refill "
               "returns to real time. Slow macro push in across the surface of the water.",
        audio="lapping water, droplets, the low stone scrape of the bowl being lifted and set "
              "down, water pouring, nothing else",
        transition="Out on the refilled bowl stilling, cut interior to 09.",
    ),
    dict(
        id="09", slug="personalized_meal", outputs=["video"],
        title="PERSONALIZED MEAL", chapter="CARE",
        scroll=(0.58, 0.64), duration="5-7s", lens="50mm + macro", ratio="2.39:1",
        mode="INT", light="interior_day", negative_space="left third",
        overlay=["YOUR ROUTINE.", "OUR PRIORITY."],
        subject="A concierge preparing and serving this specific dog's meal.",
        scene="A calm preparation area — honed stone counter, pale oak cabinetry, one warm "
              "pendant, no stainless-steel commercial-kitchen look and no restaurant styling. "
              "The dog's own labelled container sits open. A measuring scoop levelled off, not "
              "heaped. A small portion of supplement added from a marked jar. A written card on "
              "the counter with this dog's feeding notes, angled so text stays unreadable. The "
              "prepared cream bowl is carried through into the suite and set down on the oak "
              "ledge. The dog waits, sitting, eyes on the bowl but holding position until the "
              "hand withdraws and releases it.",
        camera="50mm for the preparation and the placement; 100mm macro inserts on the scoop, "
               "the label, and the food landing in the bowl.",
        motion="Static locked-off macro inserts intercut with one slow handheld-stabilised follow "
               "as the bowl is carried. Settle wide as the dog is released to eat.",
        audio="dry food into stoneware, a lid twisting, a scoop levelled, the bowl touching "
              "wood, one tail thump",
        transition="Out on the dog beginning to eat, cut to 10.",
    ),
    dict(
        id="10", slug="concierge_care", outputs=["video"],
        title="CONCIERGE CARE", chapter="CARE",
        scroll=(0.64, 0.70), duration="5-7s", lens="85mm", ratio="2.39:1",
        mode="INT", light="interior_day", negative_space="upper right",
        overlay=["CARE THAT FEELS PERSONAL."],
        subject="One-on-one attention, told in four close moments.",
        scene="A short suite of portrait-scale moments in and just outside the suite. A soft "
              "bristle brush drawn down the dog's flank, fur lifting and settling, the dog "
              "leaning into the pressure. A damp cloth folded around each front paw in turn "
              "after the walk, the paw lifted gently and given back. Two fingers slipped under "
              "the leather collar to check the fit at the throat. A blanket shaken once and laid "
              "over the bed. At the end, the concierge sits back on their heels and simply rests "
              "a hand on the dog's shoulder, looking at the dog, not at the camera — and the dog "
              "closes its eyes.",
        camera="85mm, f/1.8, warm natural window light from one side, deep falloff. Portrait "
               "framing throughout — hands, faces, fur, nothing wide.",
        motion="Minimal camera movement. Tiny drifting push-ins only. Let the performance carry "
               "it; rack focus between the hand and the dog's eye on the final beat.",
        audio="brush through coat, cloth, a collar tag, slow breathing settling, single sustained "
              "cello note",
        transition="Out on the closed eyes, cut to 11.",
    ),
    dict(
        id="11", slug="owner_update", outputs=["video"],
        title="OWNER UPDATE", chapter="PEACE OF MIND",
        scroll=(0.70, 0.75), duration="4-6s", lens="50mm", ratio="2.39:1",
        mode="INT", light="interior_day", negative_space="right third — reserve for UI overlay",
        overlay=["PEACE OF MIND.", "EVEN WHEN YOU'RE AWAY."],
        subject="A concierge photographing the resting dog to send home.",
        scene="The dog lies in the window light of its suite, chin down, awake, entirely "
              "unbothered. The concierge crouches at a low angle and lifts a phone, taking care "
              "with the framing rather than snapping. Then the reverse: the phone held at a "
              "three-quarter angle to camera, screen visible but deliberately soft and "
              "underexposed — a warm image shape on it, no readable interface, no legible text. "
              "The screen must be a clean surface the website can composite its own UI onto "
              "later. Never point the screen flat at the lens.",
        camera="50mm, f/2.0, soft interior light. Two setups only: over the shoulder onto the "
               "dog, then a low three-quarter on the phone with the dog soft in the background.",
        motion="Slow push toward the phone with a rack focus from the screen to the dog behind "
               "it, so the real thing resolves as the picture goes soft.",
        audio="a single quiet camera shutter, fabric, breathing, room tone",
        transition="Out on the rack to the dog, dissolving into 12.",
    ),
    dict(
        id="12", slug="afternoon_rest", outputs=["video"],
        title="REST / AFTERNOON NAP", chapter="REST",
        scroll=(0.75, 0.80), duration="6-8s", lens="85mm", ratio="2.39:1",
        mode="INT", light="interior_day", negative_space="upper left",
        overlay=["REST IS PART OF THE EXPERIENCE."],
        subject="The hero dog asleep on its own bed.",
        scene="The suite, quiet. The dog is fully asleep on the linen bed, on its side, one front "
              "paw extended past the edge, flank rising and falling. A long warm bar of sun lies "
              "across the bed and the floor, dust turning slowly in it. A loose linen curtain at "
              "the window lifts and settles on a breath of air, sliding the light a few "
              "centimetres across the dog and back. Nothing else in the frame moves. The room "
              "feels like a room where nothing bad happens.",
        camera="85mm, f/1.4, extremely shallow — the dog's shoulder and ribs sharp, the far side "
               "of the room dissolved.",
        motion="Very slow dolly-in over the full duration, no more than a quarter metre total. "
               "Breathing, curtain, light, dust. Nothing else. Resist every urge to add a beat.",
        audio="deep slow dog breathing, a curtain touching plaster, distant muffled birdsong, "
              "near-silence, one low piano note held and allowed to decay",
        transition="Out slowly. Cut to the widest exterior of the film for 13.",
    ),
    dict(
        id="13", slug="golden_hour", outputs=["image", "video"],
        title="GOLDEN HOUR", chapter="GOLDEN HOUR",
        scroll=(0.80, 0.87), duration="6-8s", lens="35mm", ratio="2.39:1",
        mode="EXT", light="golden", negative_space="upper left sky",
        overlay=["LUXURY STAYS.", "GROUNDED IN NATURE."],
        subject="The hero dog on a canyon overlook at the end of the day, concierge nearby.",
        scene="The most cinematic frame in the set. The dog stands square on a flat sandstone "
              "shelf at the property's overlook, facing three-quarters into a low sun that is "
              "sitting directly behind the far ridgeline. Its coat goes to pure rim-light, every "
              "guard hair separated and burning. Shadows run enormously long across the rock "
              "toward camera. Sage and grass heads catch the same backlight and glow. The "
              "concierge stands well back and to one side, a calm dark silhouette, not the "
              "subject — present, not hovering. Warm haze and floating dust fill the air.",
        camera="35mm, f/2.8, shooting into the sun with natural anamorphic-adjacent flare and a "
               "soft warm veil across the shadow side. Horizon low in frame, sky given the top "
               "half.",
        motion="Slow orbit around the dog of no more than 25 degrees, letting the sun travel the "
               "frame and clip behind the dog's head at the midpoint for a natural flare bloom. "
               "Wind moves the coat and the grasses continuously.",
        audio="wind over open rock, grasses, a single distant hawk, the full acoustic theme "
              "arriving for the only time in the film",
        transition="Out as the sun drops behind the ridge, dissolving into the blue of 14.",
    ),
    dict(
        id="14", slug="evening_retreat", outputs=["video"],
        title="EVENING RETREAT", chapter="EVENING",
        scroll=(0.87, 0.91), duration="5-8s", lens="35mm", ratio="2.39:1",
        mode="EXT", light="dusk", negative_space="upper band / deep blue sky",
        overlay=[],
        subject="The property turning over into evening, dog and concierge walking home.",
        scene="Blue hour. The sky has gone deep and clean, the last warmth draining off the "
              "canyon rim. Low path lights come up along the decomposed-granite walk — warm, "
              "shielded, pointed at the ground. The tall suite windows glow amber from inside "
              "and read as the warmest thing in frame. The concierge and the hero dog walk away "
              "from camera down the path toward the building, both unhurried, the leash slack "
              "and swinging. Their silhouettes are dark against the lit glass they are walking "
              "toward.",
        camera="35mm, f/2.0. Behind them, at hip height, centred on the path.",
        motion="Slow tracking shot from behind, following at their pace, gradually falling "
               "slightly back so the building opens up around them. No camera shake.",
        audio="footsteps and nails on granite, collar hardware, crickets starting, a door "
              "opening far ahead, low strings",
        transition="Out as they reach the door. Cut inside for 15.",
    ),
    dict(
        id="15", slug="bedtime", outputs=["video"],
        title="BEDTIME", chapter="EVENING",
        scroll=(0.91, 0.94), duration="5-7s", lens="50mm", ratio="2.39:1",
        mode="INT", light="interior_lamp", negative_space="left third",
        overlay=[],
        subject="The last check of the night.",
        scene="The suite under one warm low lamp. The dog turns twice and drops onto the bed with "
              "a sigh. The concierge lays the dog's own blanket over its hindquarters and "
              "smooths it once, crouches to touch two fingers to the water bowl and confirm it "
              "is full, then reaches and brings the lamp down to a low ember glow. A last look "
              "back from the doorway — a quiet goodnight given entirely in body language, no "
              "speech needed. The door eases almost closed, left an inch open, and warm light "
              "from the corridor lies in a thin line across the floor.",
        camera="50mm, f/1.8. Lamp-lit, deep shadow, no fill from camera side.",
        motion="Slow push-in toward the bed through the whole beat, holding as the staff member "
               "exits frame and the door closes to leave the dog alone, asleep, and safe.",
        audio="blanket, water moving in a bowl, a dimmer, a latch not quite catching, one long "
              "exhale from the dog, silence",
        transition="Out on the strip of corridor light. Match cut to morning sun in 16.",
    ),
    dict(
        id="16", slug="morning", outputs=["video"],
        title="MORNING LIGHT", chapter="MORNING",
        scroll=(0.94, 0.965), duration="5-7s", lens="50mm", ratio="2.39:1",
        mode="INT", light="morning", negative_space="upper right",
        overlay=[],
        subject="The hero dog waking up to a new day.",
        scene="The same suite, the same bed, a different hour. Clean early sun comes in low and "
              "lays a hard-edged warm rectangle across the floor and up onto the bed. The dog "
              "wakes the way dogs actually do — eyes open first and stay still, then a huge "
              "front-leg stretch with the chest dropped and the back arched, a shake that starts "
              "at the ears and runs to the tail, tail already moving. The suite door opens. A "
              "concierge steps in with the leash over one shoulder. The dog is up before the "
              "door has finished swinging.",
        camera="50mm, f/2.0, clean commercial look, slightly cooler in the shadows than the "
               "afternoon material to sell the hour.",
        motion="Slow dolly-in that begins on the bar of light on the floor and rises to find the "
               "dog as it stretches. Settle wide enough to take the open door and the incoming "
               "staff member in one frame.",
        audio="birds, a shake with the collar rattling, nails on stone, a door, the theme "
              "restating lightly",
        transition="Out on the dog heading for the door. Cut exterior to 17.",
    ),
    dict(
        id="17", slug="reunion", outputs=["video"],
        title="REUNION", chapter="REUNION",
        scroll=(0.965, 0.985), duration="5-8s", lens="50mm", ratio="2.39:1",
        mode="EXT", light="afternoon", negative_space="upper left",
        overlay=["WELCOME HOME."],
        subject="Owner and dog, back together, in the entrance court.",
        scene="The same entrance court as 02, closing the loop. The owner comes through the gate. "
              "The dog's whole body changes in one frame — the head lifts, the ears come forward, "
              "the tail goes. It crosses the stone at a fast trot, not a movie-slow-motion "
              "gallop, and shoves its head straight into the owner's hands. The owner is already "
              "down on one knee by the time it arrives. The concierge stands back, holding the "
              "leash, and lets the moment belong to them. Real, slightly messy, over in seconds. "
              "No tears, no swelling strings, no slow-motion.",
        camera="50mm, f/2.0, gently stabilised handheld with a real human weight to it — the only "
               "handheld shot in the film. Soft backlight behind the pair.",
        motion="Follow the dog across the court, settle low as the owner kneels, and hold. Let it "
               "run slightly long and end on stillness rather than on the peak of the excitement.",
        audio="fast paws on stone, one single happy vocalisation, a laugh, collar hardware, the "
              "music dropping out almost entirely for two seconds",
        transition="Out on the pair holding still together. Pull back for the final hero.",
    ),
    dict(
        id="18", slug="final_hero", outputs=["image", "video"],
        title="FINAL HERO / RETURN TO NATURE", chapter="CLOSE",
        scroll=(0.985, 1.00), duration="6-8s", lens="35mm", ratio="2.39:1",
        mode="EXT", light="golden", negative_space="entire left half and lower third — "
                                                    "reserve for wordmark and three CTAs",
        overlay=["CANYON & COLLAR", "LUXURY STAYS.", "GROUNDED IN NATURE."],
        subject="The hero dog alone in front of the property at the end of the day.",
        scene="The closing frame, composed as a poster. The dog sits calm and square on the "
              "decomposed-granite path, positioned right of centre on the third, facing camera, "
              "the leather collar catching a last edge of brass light. Behind it, the Canyon & "
              "Collar building sits low and warm against the canyon, interior lights just "
              "beginning to register against the golden sky. No staff. No other dogs. The entire "
              "left half of frame is quiet, uncluttered landscape and sky — deliberately empty, "
              "held for the wordmark, the tagline and the booking calls to action. Nothing "
              "crosses that area: no branches, no fence line, no bright highlight.",
        camera="35mm, f/4, on the path axis, dog at eye level. Horizon a third up. Nothing "
               "converging into the reserved left half.",
        motion="Very slow dolly-in over the full duration, ending with the dog centred in its "
               "third and the negative space intact. The dog holds, blinks, and lets the frame "
               "settle. End on a clean hold long enough to build the CTA over.",
        audio="the widest ambience in the film, breeze, one distant bird, the theme resolving to "
              "a single held chord and one final collar-tag chime",
        transition="Final frame. Hold, do not fade — the website holds this frame under the CTA.",
    ),
    dict(
        id="19", slug="signature_collar_macro", outputs=["image", "video"],
        title="SIGNATURE BRAND SHOT — COLLAR MACRO", chapter="BRAND",
        scroll=None, duration="4-6s", lens="100mm macro", ratio="16:9",
        mode="MACRO", light="macro", negative_space="right two-thirds",
        overlay=["CANYON & COLLAR", "LUXURY STAYS. GROUNDED IN NATURE."],
        subject="The collar itself, as an object.",
        scene="Extreme macro on the Canyon & Collar collar laid on warm stone. Aged brown "
              "leather, genuinely worn: open pores, a burnished edge where it has rubbed, "
              "slight colour variation along the strap, honest creasing at the buckle holes. "
              "Matte brass hardware with fine micro-scratches and one warm specular highlight "
              "travelling across it. A small brass tag carries a shallow, physically believable "
              "engraving — CANYON & COLLAR, and beneath it in smaller letters LUXURY STAYS. "
              "GROUNDED IN NATURE. The engraving must read as struck into metal: crisp walls, a "
              "darker oxidised base, a bright catching edge where the light crosses it, letters "
              "slightly uneven in depth. Never flat printed, never embossed, never glowing.",
        camera="100mm macro, f/4 for enough depth to hold the tag face, focus stacked feel. "
               "Single warm key from the upper left, black negative fill opposite.",
        motion="Slow macro drift along the strap, the specular highlight travelling across the "
               "brass, arriving to settle on the tag with the engraving resolving into focus at "
               "the end. Alternatively reverse it for use as a transition wipe.",
        audio="pure near-silence, one leather creak, one brass tick, a single low sustained tone",
        transition="Designed as a reusable interstitial — cut in anywhere as a palate cleanser "
                   "or scroll transition.",
    ),
]


def filebase(a, kind):
    """Output filename per the agreed naming convention."""
    if len(a["outputs"]) > 1:
        return f'{a["id"]}_{a["slug"]}_{kind}'
    return f'{a["id"]}_{a["slug"]}'


def poster_base(a):
    """Every asset gets a still plate — video-only assets use a _poster suffix."""
    if "image" in a["outputs"]:
        return filebase(a, "image")
    return f'{a["id"]}_{a["slug"]}_poster'


# ---------------------------------------------------------------------------
# Camera moves, expressed as SVG viewBox keyframes so the proxy renders stay
# vector-sharp at every zoom level. z = magnification, x/y = frame offset as a
# percentage of frame width/height. These mirror the "Motion" note in each
# prompt brief, so an approved proxy move can be handed straight to the DP.
# ---------------------------------------------------------------------------
MOVES = {
    "01": dict(dur=7.0, z=(1.00, 1.09), x=(0.0, 0.0),  y=(0.0, 0.0),  ease="inout", note="slow dolly-in"),
    "02": dict(dur=6.0, z=(1.10, 1.10), x=(-3.0, 3.0), y=(0.0, 0.0),  ease="inout", note="lateral track"),
    "03": dict(dur=5.0, z=(1.02, 1.30), x=(2.0, -4.0), y=(0.0, 2.0),  ease="in",    note="macro push to buckle"),
    "04": dict(dur=7.0, z=(1.02, 1.14), x=(2.0, -2.0), y=(0.0, 0.0),  ease="inout", note="dolly through doorway"),
    "05": dict(dur=5.0, z=(1.12, 1.12), x=(3.0, -3.0), y=(0.0, 0.0),  ease="inout", note="slider"),
    "06": dict(dur=8.0, z=(1.08, 1.08), x=(-5.0, 5.0), y=(0.0, 0.0),  ease="linear", note="walking track"),
    "07": dict(dur=6.0, z=(1.06, 1.10), x=(5.0, -4.0), y=(0.0, -1.0), ease="inout", note="track with run-past"),
    "08": dict(dur=5.0, z=(1.05, 1.28), x=(-2.0, 2.0), y=(1.0, -1.0), ease="inout", note="macro push on water"),
    "09": dict(dur=6.0, z=(1.03, 1.12), x=(-2.0, 1.0), y=(0.0, 0.0),  ease="inout", note="follow the bowl"),
    "10": dict(dur=6.0, z=(1.04, 1.12), x=(1.0, -1.0), y=(0.0, 0.0),  ease="inout", note="drifting push-in"),
    "11": dict(dur=5.0, z=(1.03, 1.16), x=(3.0, -2.0), y=(0.0, 0.0),  ease="inout", note="push to phone, rack"),
    "12": dict(dur=7.0, z=(1.02, 1.07), x=(0.0, 0.0),  y=(0.0, 0.0),  ease="inout", note="barely-there dolly"),
    "13": dict(dur=7.0, z=(1.06, 1.12), x=(-4.0, 4.0), y=(1.0, -1.0), ease="inout", note="slow orbit"),
    "14": dict(dur=6.0, z=(1.00, 1.10), x=(0.0, 0.0),  y=(0.0, 1.0),  ease="inout", note="track from behind"),
    "15": dict(dur=6.0, z=(1.02, 1.14), x=(-2.0, 1.0), y=(0.0, 0.0),  ease="inout", note="push-in to bed"),
    "16": dict(dur=6.0, z=(1.10, 1.02), x=(0.0, 0.0),  y=(3.0, -2.0), ease="inout", note="rise from floor light"),
    "17": dict(dur=6.0, z=(1.12, 1.04), x=(3.0, -1.0), y=(0.0, 1.0),  ease="out",   note="follow and settle",
               handheld=True),
    "18": dict(dur=7.0, z=(1.00, 1.08), x=(0.0, 0.0),  y=(0.0, 0.0),  ease="inout", note="final slow dolly-in"),
    "19": dict(dur=5.0, z=(1.04, 1.26), x=(-3.0, 3.0), y=(1.0, -2.0), ease="inout", note="macro drift to tag"),
}
