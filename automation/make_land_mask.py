#!/usr/bin/env python3
"""Approximate equirectangular land mask (white land, transparent ocean), 1024x512.
Continents drawn from (lon,lat) polygons -> recognizable silhouettes for the hero
globe. This is a hand-approximation (a stopgap); replace assets/textures/earth-land.png
with a real equirectangular land map for exact coastlines.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

W, H = 1024, 512
im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
WHITE = (255, 255, 255, 255)

def px(lon, lat):
    return ((lon + 180) / 360.0 * W, (90 - lat) / 180.0 * H)

continents = {
 "N_AMERICA": [(-166,60),(-158,68),(-130,70),(-100,72),(-84,73),(-62,60),(-56,52),(-66,47),(-80,44),(-81,30),(-90,29),(-97,25),(-107,23),(-114,30),(-124,40),(-124,48),(-130,54),(-150,59),(-166,60)],
 "C_AMERICA": [(-92,18),(-83,15),(-78,9),(-82,8),(-90,13),(-95,16)],
 "GREENLAND": [(-46,60),(-20,70),(-18,80),(-40,83),(-60,80),(-56,68)],
 "S_AMERICA": [(-79,9),(-60,11),(-50,0),(-35,-6),(-38,-14),(-48,-25),(-54,-34),(-66,-52),(-73,-52),(-71,-40),(-76,-18),(-81,-4),(-79,9)],
 "AFRICA": [(-16,15),(-11,22),(-6,33),(10,37),(24,33),(33,31),(43,12),(51,11),(48,-2),(40,-16),(33,-28),(20,-35),(14,-24),(9,-2),(8,5),(-8,5),(-16,15)],
 "EUROPE": [(-10,37),(-9,44),(-2,49),(3,52),(0,59),(12,58),(26,60),(40,60),(30,47),(28,41),(20,40),(12,37),(-10,37)],
 "ASIA": [(40,60),(60,70),(90,76),(120,76),(145,72),(160,66),(150,60),(140,52),(135,44),(122,40),(122,30),(110,20),(105,10),(97,10),(92,22),(80,8),(77,20),(67,24),(57,26),(45,40),(40,50),(40,60)],
 "ARABIA": [(33,30),(43,12),(52,18),(57,22),(48,30),(38,32)],
 "INDONESIA": [(95,6),(108,2),(120,0),(140,-4),(150,-8),(132,-8),(118,-9),(104,-4),(96,-1)],
 "AUSTRALIA": [(114,-22),(129,-12),(137,-12),(143,-11),(150,-24),(153,-31),(146,-38),(138,-35),(129,-32),(115,-34),(113,-26)],
 "ANTARCTICA": [(-180,-90),(180,-90),(180,-68),(120,-66),(40,-69),(-40,-66),(-120,-70),(-180,-68)],
 "JAPAN": [(130,31),(136,34),(141,40),(143,44),(139,37),(133,33)],
 "UK": [(-6,50),(-2,53),(-3,58),(-8,57),(-7,52)],
 "NZ": [(166,-40),(174,-36),(178,-42),(170,-47),(166,-42)],
 "MADAGASCAR": [(43,-13),(50,-16),(48,-25),(44,-22)],
}
for pts in continents.values():
    d.polygon([px(a, b) for a, b in pts], fill=WHITE)

# slight smoothing so coastlines are not hard-edged, then re-threshold to crisp
alpha = im.split()[3].filter(ImageFilter.GaussianBlur(1.4))
im.putalpha(alpha.point(lambda a: 255 if a > 90 else 0))

out = Path("C:/Users/Ahmed/Claude_Projects/Mohd-Faizuddin-Ahmed/assets/textures/earth-land.png")
out.parent.mkdir(parents=True, exist_ok=True)
im.save(out, "PNG")
print(f"land mask v2: {out} ({out.stat().st_size} bytes, {W}x{H})")
