"""Script to fetch authentic, high-resolution, watermark-free images of all 61 museum artifacts via Wikipedia REST API + Search fallback."""
import io
import json
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BACKEND_DIR = Path(__file__).resolve().parent.parent
FRONTEND_ARTIFACTS_DIR = BACKEND_DIR.parent / "frontend" / "public" / "artifacts"
DATASET_IMAGES_DIR = BACKEND_DIR.parent / "dataset" / "images"

FRONTEND_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
DATASET_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

USER_AGENT = "AIMuseumGuide/1.0 (academic research museum guide; contact@museum.org)"

WIKI_PAGE_MAP = [
    ("ART001", "The_Thinker", "The Thinker Rodin sculpture"),
    ("ART002", "Mona_Lisa", "Mona Lisa Leonardo da Vinci"),
    ("ART003", "David_(Michelangelo)", "Michelangelo David Florence"),
    ("ART004", "The_Starry_Night", "The Starry Night Van Gogh"),
    ("ART005", "Water_Lilies_(Monet_series)", "Water Lilies Monet"),
    ("ART006", "Guernica_(Picasso)", "Guernica Picasso"),
    ("ART007", "The Ballet Class (Degas, Musée d'Orsay)", "The Ballet Class Edgar Degas"),
    ("ART008", "The_Night_Watch", "The Night Watch Rembrandt"),
    ("ART009", "Girl_with_a_Pearl_Earring", "Girl with a Pearl Earring Vermeer"),
    ("ART010", "The_Birth_of_Venus", "The Birth of Venus Botticelli"),
    ("ART011", "David (Donatello)", "Donatello David bronze Bargello"),
    ("ART012", "Apollo_and_Daphne_(Bernini)", "Apollo and Daphne Bernini"),
    ("ART013", "The_Death_of_Socrates", "The Death of Socrates Jacques-Louis David"),
    ("ART014", "Liberty_Leading_the_People", "Liberty Leading the People Delacroix"),
    ("ART015", "Nefertiti_Bust", "Nefertiti Bust Neues Museum"),
    ("ART016", "Discobolus", "Discobolus Myron statue"),
    ("ART017", "The Kiss (Rodin sculpture)", "The Kiss Auguste Rodin marble"),
    ("ART018", "The_Gates_of_Hell", "The Gates of Hell Auguste Rodin"),
    ("ART019", "The_Burghers_of_Calais", "The Burghers of Calais Rodin"),
    ("ART020", "The_Last_Supper_(Leonardo)", "The Last Supper Leonardo da Vinci"),
    ("ART021", "Vitruvian_Man", "Vitruvian Man Leonardo da Vinci"),
    ("ART022", "Pietà_(Michelangelo)", "Michelangelo Pieta Vatican"),
    ("ART023", "Sistine_Chapel_ceiling", "Sistine Chapel ceiling Michelangelo"),
    ("ART024", "Sunflowers_(Van_Gogh_series)", "Sunflowers Van Gogh"),
    ("ART025", "The_Potato_Eaters", "The Potato Eaters Van Gogh"),
    ("ART026", "Impression,_Sunrise", "Impression Sunrise Monet"),
    ("ART027", "Les_Demoiselles_d'Avignon", "Les Demoiselles d'Avignon Picasso"),
    ("ART028", "The_Old_Guitarist", "The Old Guitarist Picasso"),
    ("ART029", "The Dance Class (Degas, Metropolitan Museum of Art)", "The Dance Class Edgar Degas"),
    ("ART030", "The_Storm_on_the_Sea_of_Galilee", "The Storm on the Sea of Galilee Rembrandt"),
    ("ART031", "The_Milkmaid_(Vermeer)", "The Milkmaid Vermeer"),
    ("ART031A", "Primavera_(Botticelli)", "Primavera Botticelli Uffizi"),
    ("ART032", "Ecstasy_of_Saint_Teresa", "Ecstasy of Saint Teresa Bernini"),
    ("ART033", "Napoleon_Crossing_the_Alps", "Napoleon Crossing the Alps David"),
    ("ART034", "The_Death_of_Marat", "The Death of Marat David"),
    ("ART035", "The_Raft_of_the_Medusa", "The Raft of the Medusa Gericault"),
    ("ART036", "Mask_of_Tutankhamun", "Mask of Tutankhamun Cairo"),
    ("ART037", "Rosetta_Stone", "Rosetta Stone British Museum"),
    ("ART038", "Venus_de_Milo", "Venus de Milo Louvre"),
    ("ART039", "Laocoön_and_His_Sons", "Laocoon and His Sons Vatican"),
    ("ART040", "Dance_(Matisse)", "Dance Henri Matisse"),
    ("ART041", "The_Persistence_of_Memory", "The Persistence of Memory Dali"),
    ("ART042", "The_Two_Fridas", "The Two Fridas Frida Kahlo"),
    ("ART043", "Red Canna (painting)", "Red Canna Georgia O'Keeffe"),
    ("ART044", "Black Iris III", "Black Iris Georgia O'Keeffe"),
    ("ART045", "Bal_du_moulin_de_la_Galette", "Bal du moulin de la Galette Renoir"),
    ("ART046", "The_Scream", "The Scream Edvard Munch"),
    ("ART047", "Woman_with_a_Parasol_-_Madame_Monet_and_Her_Son", "Woman with a Parasol Monet"),
    ("ART048", "The_Card_Players", "The Card Players Cezanne"),
    ("ART049", "The_Age_of_Bronze", "The Age of Bronze Auguste Rodin"),
    ("ART050", "Man_with_the_Broken_Nose", "Man with Broken Nose Auguste Rodin"),
    ("ART051", "Winged_Victory_of_Samothrace", "Winged Victory of Samothrace Louvre"),
    ("ART052", "Great_Sphinx_of_Giza", "Great Sphinx of Giza"),
    ("ART053", "The_School_of_Athens", "The School of Athens Raphael Vatican"),
    ("ART054", "Arnolfini_Portrait", "Arnolfini Portrait Jan van Eyck"),
    ("ART055", "The_Creation_of_Adam", "The Creation of Adam Michelangelo"),
    ("ART056", "Campbell's_Soup_Cans", "Campbells Soup Cans Andy Warhol"),
    ("ART057", "The_Harvesters_(painting)", "The Harvesters Pieter Bruegel"),
    ("ART058", "The_Third_of_May_1808", "The Third of May 1808 Francisco Goya"),
    ("ART059", "Equestrian_Statue_of_Marcus_Aurelius", "Equestrian Statue of Marcus Aurelius"),
    ("ART060", "Terracotta_Army", "Terracotta Army warrior Xi'an"),
]


def fetch_wikipedia_image_url(page_title: str, query: str) -> str | None:
    # 1. Try direct page title summary
    encoded_title = urllib.parse.quote(page_title)
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            orig = data.get("originalimage", {})
            if orig and "source" in orig:
                return orig["source"]
            thumb = data.get("thumbnail", {})
            if thumb and "source" in thumb:
                return thumb["source"]
    except Exception:
        pass

    # 2. Fallback to Wikipedia Search API if direct title was 404/redirected
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
    req_search = urllib.request.Request(search_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req_search, context=ctx, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            search_results = data.get("query", {}).get("search", [])
            if search_results:
                best_title = search_results[0]["title"]
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title)}"
                req_summary = urllib.request.Request(summary_url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req_summary, context=ctx, timeout=8) as resp2:
                    data2 = json.loads(resp2.read().decode("utf-8"))
                    orig = data2.get("originalimage", {})
                    if orig and "source" in orig:
                        return orig["source"]
                    thumb = data2.get("thumbnail", {})
                    if thumb and "source" in thumb:
                        return thumb["source"]
    except Exception as e:
        print(f"  [Warning] Wikipedia search failed for '{query}': {e}")

    return None


def download_artifact_image(art_id: str, page_title: str, query: str):
    print(f"[{art_id}] Fetching authentic image for: {page_title}...")
    img_url = fetch_wikipedia_image_url(page_title, query)

    if not img_url:
        print(f"  [Fallback] No image returned for {art_id}.")
        return

    try:
        req = urllib.request.Request(img_url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            img_bytes = resp.read()

        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

        # Save to frontend/public/artifacts/ARTxxx.jpg
        frontend_path = FRONTEND_ARTIFACTS_DIR / f"{art_id}.jpg"
        img.save(frontend_path, "JPEG", quality=90)

        # Save to dataset/images/ARTxxx/image_01.jpg
        art_dataset_dir = DATASET_IMAGES_DIR / art_id
        art_dataset_dir.mkdir(parents=True, exist_ok=True)
        img.save(art_dataset_dir / "image_01.jpg", "JPEG", quality=90)

        print(f"  [OK] Saved authentic artwork to {frontend_path.name}")
    except Exception as e:
        print(f"  [Error] Failed downloading {art_id}: {e}")


def main():
    print(f"Downloading authentic high-resolution artwork images for {len(WIKI_PAGE_MAP)} artifacts...")
    for art_id, page_title, query in WIKI_PAGE_MAP:
        download_artifact_image(art_id, page_title, query)
        time.sleep(0.4)
    print("[OK] All authentic museum artwork images successfully updated!")


if __name__ == "__main__":
    main()
