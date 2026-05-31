Create one horizontal animation strip for Codex pet `qiqi`, state `waiting`.

Use the attached canonical base for identity. Use the attached layout guide only for slot count, spacing, centering, and padding; do not draw the guide.

Output exactly 6 full-body frames in one left-to-right row on flat pure magenta #FF00FF. Treat the row as 6 invisible equal-width slots: one centered complete pose per slot, evenly spaced, with no overlap, clipping, empty slots, labels, or borders.

Identity: same pet in every frame: Qiqi is a lively silver tabby-and-white young cat with amber round eyes, white chest and white paws, dark forehead stripes, short plush fur, playful parkour energy, loves shrimp and chasing soft balls; calm pose is loafing or lying in a round cat bed by the window.. Preserve silhouette, face, proportions, markings, palette, material, style, and props.
Style: Pet-safe sprite: compact full-body mascot, readable in a 192x208 cell, clear silhouette, simple face, stable palette/materials, and crisp edges for chroma-key extraction. Style `sticker`: Polished sticker mascot with bold clean shapes, crisp outline, flat colors, and minimal highlight detail. User style notes: match Mantou output: soft cute sticker style, rounded compact whole-body silhouette, crisp clean outline, readable at tiny desktop pet size; preserve Qiqi silver tabby stripes, white chest and paws, amber eyes, small pink-brown nose, lively alert expression; optional tiny shrimp or soft ball may appear only when state-appropriate and attached/held, no text..
Animation continuity: keep apparent pet scale and baseline stable within the row unless the state itself intentionally changes vertical position, such as `jumping`. Move the pose within the slot instead of redrawing the pet larger or smaller frame to frame.

State action: Needs-input loop: expectant asking pose for approval, help, or user input.

State requirements:
- Show that Codex needs approval, help, or user input through an expectant asking pose.
- Keep the motion patient and readable, without turning it into ordinary idle or review.

Clean extraction: crisp opaque edges, safe padding, no scenery, text, guide marks, checkerboard, shadows, glows, motion blur, speed lines, dust, detached effects, stray pixels, or chroma-key colors inside the pet.
