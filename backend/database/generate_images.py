"""Generate controlled museum artifact image dataset for all 60 seeded artifacts."""
import io
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
PUBLIC_ARTIFACTS_DIR = PROJECT_ROOT / "frontend" / "public" / "artifacts"
DATASET_IMAGES_DIR = PROJECT_ROOT / "dataset" / "images"

sys.path.insert(0, str(BACKEND_DIR))
from database.seed import ARTIFACTS, ARTISTS, PERIODS

PERIOD_PALETTES = {
    "PER001": ("#1c1917", "#92400e", "#f59e0b", "Ancient Egypt"),       # Gold / Ochre / Dark stone
    "PER002": ("#0f172a", "#334155", "#94a3b8", "Classical Antiquity"), # Marble / Slate / Navy
    "PER003": ("#2a1215", "#881337", "#fbbf24", "Renaissance"),         # Crimson / Gold / Dark Wood
    "PER004": ("#1e1b18", "#78350f", "#fef08a", "Baroque"),             # Chiaroscuro Amber / Shadow
    "PER005": ("#064e3b", "#047857", "#ecfdf5", "Neoclassicism"),       # Marble Green / Emerald
    "PER006": ("#450a0a", "#991b1b", "#fca5a5", "Romanticism"),         # Dramatic Red / Storm
    "PER007": ("#0c4a6e", "#0284c7", "#bae6fd", "Impressionism"),       # Cerulean / Light Blue
    "PER008": ("#27272a", "#52525b", "#d4d4d8", "Modern Sculpture"),   # Bronze / Charcoal
    "PER009": ("#312e81", "#4f46e5", "#c7d2fe", "Modern Art"),          # Indigo / Avant-garde
    "PER010": ("#4c1d95", "#7c3aed", "#ddd6fe", "Contemporary Art"),    # Electric Violet
}

ARTIST_MAP = {a[0]: a[1] for a in ARTISTS}
PERIOD_MAP = {p[0]: p[1] for p in PERIODS}

def draw_artwork(artifact):
    art_id, name, art_type, artist_id, period_id, gallery_id, year, desc, _ = artifact
    artist_name = ARTIST_MAP.get(artist_id, "Unknown Artist")
    period_name = PERIOD_MAP.get(period_id, "Historical Period")
    
    bg_dark, bg_mid, accent, p_label = PERIOD_PALETTES.get(period_id, ("#18181b", "#3f3f46", "#e4e4e7", "Art"))

    width, height = 800, 1000
    img = Image.new("RGB", (width, height), bg_dark)
    draw = ImageDraw.Draw(img)

    # Outer museum frame
    draw.rectangle([20, 20, width - 20, height - 20], outline=accent, width=8)
    draw.rectangle([32, 32, width - 32, height - 32], outline="#52525b", width=2)

    # Canvas area
    c_left, c_top, c_right, c_bottom = 60, 60, width - 60, height - 320
    draw.rectangle([c_left, c_top, c_right, c_bottom], fill=bg_mid, outline="#27272a", width=3)

    # Visual Motif based on type
    cx, cy = (c_left + c_right) // 2, (c_top + c_bottom) // 2
    if art_type == "Sculpture":
        # Pedestal & Statue silhouette motif
        draw.polygon([(cx - 80, cy + 180), (cx + 80, cy + 180), (cx + 60, cy + 130), (cx - 60, cy + 130)], fill="#18181b", outline=accent)
        draw.ellipse([cx - 90, cy - 140, cx + 90, cy + 120], outline=accent, width=4)
        draw.polygon([(cx, cy - 160), (cx - 70, cy + 80), (cx + 70, cy + 80)], outline="#ffffff", width=2)
    elif art_type == "Painting":
        # Ornate easel & painterly concentric arcs
        for r in range(160, 20, -25):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=accent, width=3)
        draw.rectangle([cx - 140, cy - 100, cx + 140, cy + 100], outline="#ffffff", width=2)
    else:  # Drawing / Stele
        draw.rectangle([cx - 120, cy - 160, cx + 120, cy + 160], fill="#09090b", outline=accent, width=3)
        for y_line in range(cy - 120, cy + 140, 25):
            draw.line([(cx - 90, y_line), (cx + 90, y_line)], fill="#71717a", width=2)

    # Metadata Plaque Area (Bottom 280px)
    plaque_top = height - 300
    draw.rectangle([60, plaque_top, width - 60, height - 60], fill="#09090b", outline=accent, width=3)

    # Text content on Plaque
    year_str = f"{abs(year)} BC" if year < 0 else str(year)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 34)
        font_meta = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font_title = font_meta = font_small = ImageFont.load_default()

    # Draw Title
    draw.text((80, plaque_top + 25), name, fill="#ffffff", font=font_title)
    
    # Draw Artist & Year
    draw.text((80, plaque_top + 75), f"Artist: {artist_name} ({year_str})", fill=accent, font=font_meta)
    
    # Draw Period & Type
    draw.text((80, plaque_top + 115), f"Period: {period_name}  |  Type: {art_type}", fill="#a1a1aa", font=font_meta)
    
    # Draw Description snippet
    desc_snippet = desc[:90] + "..." if len(desc) > 90 else desc
    draw.text((80, plaque_top + 160), f'"{desc_snippet}"', fill="#71717a", font=font_small)
    
    # Museum Badge
    draw.text((width - 240, height - 90), f"AI MUSEUM • {art_id}", fill=accent, font=font_small)

    return img

def main():
    PUBLIC_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating images for {len(ARTIFACTS)} artifacts...")
    for art in ARTIFACTS:
        art_id = art[0]
        img = draw_artwork(art)
        
        # Save to public/artifacts/{art_id}.jpg
        pub_path = PUBLIC_ARTIFACTS_DIR / f"{art_id}.jpg"
        img.save(pub_path, "JPEG", quality=90)
        
        # Save to dataset/images/{art_id}/image_01.jpg
        ds_dir = DATASET_IMAGES_DIR / art_id
        ds_dir.mkdir(parents=True, exist_ok=True)
        img.save(ds_dir / "image_01.jpg", "JPEG", quality=90)

    print(f"Successfully generated 60 images in {PUBLIC_ARTIFACTS_DIR} and {DATASET_IMAGES_DIR}")

if __name__ == "__main__":
    main()
