# Hero globe — land mask

`earth-land.png` is the equirectangular land mask the hero globe
(`assets/js/hero-globe.js`) samples so the teal dots trace the continents. It
is loaded at runtime; if it is missing or fails, the globe falls back to an
even sphere.

**Current file:** a real, accurate world land mask (white land on transparent
ocean, 2:1 equirectangular, ~632×316, ~32% land). It was produced by cleaning
a supplied world map to a crisp binary silhouette (graticule/grid lines and
colour removed, keeping only near-white land).

## Replacing it

Drop a new image at this exact path (`assets/textures/earth-land.png`) matching:

- **Projection:** equirectangular (plate carrée), **2:1** aspect ratio.
- **Content:** land = **bright/near-white**, ocean = **dark or transparent**.
  The globe keeps a dot only where a pixel is opaque (alpha ≥ 40) and bright
  (brightness ≥ 90), so any high-contrast land/ocean mask works. Strip
  grid-lines / country colours first (a coloured political map will otherwise
  scatter stray dots), e.g. keep only pixels that are bright AND low-saturation.

No code change is needed — refresh and the globe re-samples the new mask.

Note: a dotted globe renders **coastlines/continents**, not thin country
**border lines** (dots can't resolve 1px borders).
