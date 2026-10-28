# Sketch: light-driven exchange as a state axis (not wired)

Co-authored, 2026-10-28. CC0. Does not run; not imported.

Occasion: ACS Nano 2026-10-23, doi:10.1021/acsnano.6c06828 (Monash).
First-principles prediction, press depth: THz light -> confined
magnetophononic polaritons -> interlayer exchange change -> 2-SL MnBi2Te4
goes AFM/trivial (OFF) -> FM/edge-conducting (ON). Untested by experiment.

## What S would need

```
S_Si   = (n, d, l, k_e, k_o, k_t, k_m)          current, Si-scoped
S_mag  = S_Si + (J_inter, C)                    sketch only
           J_inter : interlayer exchange, sign sets AFM (<0) vs FM (>0)
           C       : Chern number, integer, read from the band structure
```

Candidate morphism (none registered):

```
drive (THz, phonon-resonant) --polariton--> delta J_inter --sign flip--> C: 0 -> 1
```

## Gates before promotion (sketches/README criteria apply)

| gate | state |
|---|---|
| 2-SL gap value from the paper | NOT_IN_TEXT (press depth) |
| operating temperature vs T_N (~24 K bulk, VERIFY) | Bridge TSW-2: ceiling ~22 K |
| Fermi level inside the gap (doping as constraint) | PROPOSED, Bridge TSW-5 |
| transfer to Si | DOES_NOT_TRANSFER, Bridge TSW-4 |
| experiment | none yet |

C is an integer, so the "continuous morphism" this repo walks does not reach
it smoothly: the step is a gap closing, a discontinuity in the graph's sense.
That is the reason it is a sketch and not an edge.
