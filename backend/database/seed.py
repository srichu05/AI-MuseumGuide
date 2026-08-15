"""Seed the museum database with curated dataset."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import DATASET_DIR, DB_PATH, DOCUMENTS_DIR
from database.connection import get_connection, init_db

PERIODS = [
    ("PER001", "Ancient Egypt", -3100, -30, "Art and culture of ancient Egyptian civilization spanning pharaohs, temples, and tomb art."),
    ("PER002", "Classical Antiquity", -800, 500, "Greek and Roman art emphasizing idealized human form, mythology, and civic monuments."),
    ("PER003", "Renaissance", 1400, 1600, "European rebirth of classical learning with perspective, humanism, and master painters."),
    ("PER004", "Baroque", 1600, 1750, "Dramatic, ornate art emphasizing movement, emotion, and grandeur."),
    ("PER005", "Neoclassicism", 1750, 1850, "Return to classical simplicity, order, and republican virtue after Rococo excess."),
    ("PER006", "Romanticism", 1800, 1850, "Emphasis on emotion, nature, and individual expression against industrial rationalism."),
    ("PER007", "Impressionism", 1860, 1890, "Capturing fleeting light and modern life with visible brushstrokes and outdoor scenes."),
    ("PER008", "Modern Sculpture", 1850, 1950, "Break from tradition exploring form, material, and psychological expression in three dimensions."),
    ("PER009", "Modern Art", 1860, 1970, "Avant-garde movements challenging representation from Cubism to Abstract Expressionism."),
    ("PER010", "Contemporary Art", 1970, 2026, "Global, conceptual, and media-diverse art reflecting current society and technology."),
]

ARTISTS = [
    ("ARTIST001", "Auguste Rodin", 1840, 1917, "French", "French sculptor whose expressive bronze works revolutionized modern sculpture."),
    ("ARTIST002", "Leonardo da Vinci", 1452, 1519, "Italian", "Renaissance polymath known for Mona Lisa and anatomical studies."),
    ("ARTIST003", "Michelangelo Buonarroti", 1475, 1564, "Italian", "Master of sculpture, painting, and architecture of the High Renaissance."),
    ("ARTIST004", "Vincent van Gogh", 1853, 1890, "Dutch", "Post-Impressionist painter celebrated for bold color and emotional intensity."),
    ("ARTIST005", "Claude Monet", 1840, 1926, "French", "Founder of French Impressionism focused on light and atmosphere."),
    ("ARTIST006", "Pablo Picasso", 1881, 1973, "Spanish", "Cubist pioneer who reshaped 20th-century art across many styles."),
    ("ARTIST007", "Edgar Degas", 1834, 1917, "French", "Impressionist known for ballet dancers and dynamic compositions."),
    ("ARTIST008", "Rembrandt van Rijn", 1606, 1669, "Dutch", "Baroque master of chiaroscuro portraiture and biblical scenes."),
    ("ARTIST009", "Johannes Vermeer", 1632, 1675, "Dutch", "Dutch Golden Age painter of intimate domestic interiors and light."),
    ("ARTIST010", "Sandro Botticelli", 1445, 1510, "Italian", "Early Renaissance painter of mythological and religious allegories."),
    ("ARTIST011", "Donatello", 1386, 1466, "Italian", "Early Renaissance sculptor who revived classical bronze and marble techniques."),
    ("ARTIST012", "Gian Lorenzo Bernini", 1598, 1680, "Italian", "Baroque sculptor and architect of dramatic religious works."),
    ("ARTIST013", "Jacques-Louis David", 1748, 1825, "French", "Neoclassical painter of revolutionary and imperial themes."),
    ("ARTIST014", "Eugène Delacroix", 1798, 1863, "French", "Romantic painter of vivid color and historical drama."),
    ("ARTIST015", "Unknown Egyptian Artisan", -1500, -1500, "Egyptian", "Anonymous craftsmen of the New Kingdom creating tomb and temple art."),
    ("ARTIST016", "Unknown Greek Sculptor", -450, -400, "Greek", "Classical Greek workshop producing idealized marble figures."),
    ("ARTIST017", "Henri Matisse", 1869, 1954, "French", "Modern master of color, form, and decorative composition."),
    ("ARTIST018", "Salvador Dalí", 1904, 1989, "Spanish", "Surrealist painter of dream imagery and meticulous technique."),
    ("ARTIST019", "Frida Kahlo", 1907, 1954, "Mexican", "Painter of symbolic self-portraits exploring identity and pain."),
    ("ARTIST020", "Georgia O'Keeffe", 1887, 1986, "American", "Modern American painter of enlarged flowers and southwestern landscapes."),
]

GALLERIES = [
    ("GAL001", "Grand Atrium", 1, "East Wing", "Central entrance hall with monumental sculptures and rotating highlights."),
    ("GAL002", "Ancient Worlds Gallery", 1, "North Wing", "Egyptian, Greek, and Roman artifacts in climate-controlled cases."),
    ("GAL003", "Renaissance Hall", 2, "South Wing", "Paintings and sculptures from the Italian and Northern Renaissance."),
    ("GAL004", "Gallery of Modern Sculpture", 2, "West Wing", "Bronze and marble works from Rodin to contemporary sculptors."),
    ("GAL005", "Impressionist Salon", 2, "East Wing", "Light-filled room dedicated to French Impressionism."),
    ("GAL006", "Baroque Gallery", 3, "North Wing", "Dramatic religious and court paintings of the 17th century."),
    ("GAL007", "Contemporary Space", 3, "South Wing", "Flexible gallery for rotating contemporary exhibitions."),
    ("GAL008", "Prints & Drawings Room", 1, "Basement Level", "Works on paper displayed in low-light conservation conditions."),
]

EXHIBITIONS = [
    ("EXH001", "Masters of Bronze", "2025-01-15", "2025-06-30", "Survey of bronze sculpture from antiquity to Rodin."),
    ("EXH002", "Light and Color: Impressionism", "2025-03-01", "2025-09-01", "Impressionist paintings exploring changing light."),
    ("EXH003", "Faces of the Renaissance", "2024-09-01", "2025-02-28", "Portraiture and humanism in Renaissance art."),
    ("EXH004", "Ancient Echoes", "2025-05-01", "2025-12-31", "Cross-cultural connections in ancient Mediterranean art."),
    ("EXH005", "Modern Visions", "2025-07-01", "2026-01-31", "20th-century avant-garde movements and their legacy."),
]

ARTIFACTS = [
    ("ART001", "The Thinker", "Sculpture", "ARTIST001", "PER008", "GAL004", 1904, "Rodin's iconic bronze figure seated in deep contemplation, originally conceived for The Gates of Hell.", "/artifacts/ART001.jpg"),
    ("ART002", "Mona Lisa", "Painting", "ARTIST002", "PER003", "GAL003", 1503, "Portrait of Lisa Gherardini renowned for its enigmatic smile and sfumato technique.", "/artifacts/ART002.jpg"),
    ("ART003", "David", "Sculpture", "ARTIST003", "PER003", "GAL003", 1504, "Marble masterpiece depicting the biblical hero before his battle with Goliath.", "/artifacts/ART003.jpg"),
    ("ART004", "Starry Night", "Painting", "ARTIST004", "PER009", "GAL005", 1889, "Swirling night sky over Saint-Rémy expressing the artist's turbulent inner vision.", "/artifacts/ART004.jpg"),
    ("ART005", "Water Lilies", "Painting", "ARTIST005", "PER007", "GAL005", 1919, "Monet's serene pond series capturing reflections and atmospheric light.", "/artifacts/ART005.jpg"),
    ("ART006", "Guernica", "Painting", "ARTIST006", "PER009", "GAL007", 1937, "Monumental anti-war mural responding to the bombing of Guernica during the Spanish Civil War.", "/artifacts/ART006.jpg"),
    ("ART007", "The Ballet Class", "Painting", "ARTIST007", "PER007", "GAL005", 1874, "Rehearsal scene showing dancers at the barre with off-center composition.", "/artifacts/ART007.jpg"),
    ("ART008", "The Night Watch", "Painting", "ARTIST008", "PER004", "GAL006", 1642, "Dynamic group portrait of a civic militia company in dramatic lighting.", "/artifacts/ART008.jpg"),
    ("ART009", "Girl with a Pearl Earring", "Painting", "ARTIST009", "PER004", "GAL006", 1665, "Tronie of a girl in exotic dress with a luminous pearl earring.", "/artifacts/ART009.jpg"),
    ("ART010", "The Birth of Venus", "Painting", "ARTIST010", "PER003", "GAL003", 1485, "Mythological scene of Venus arriving at shore on a giant scallop shell.", "/artifacts/ART010.jpg"),
    ("ART011", "David (Bronze)", "Sculpture", "ARTIST011", "PER003", "GAL003", 1440, "First free-standing nude bronze since antiquity depicting youthful David.", "/artifacts/ART011.jpg"),
    ("ART012", "Apollo and Daphne", "Sculpture", "ARTIST012", "PER004", "GAL006", 1625, "Baroque marble capturing the moment Daphne transforms into a laurel tree.", "/artifacts/ART012.jpg"),
    ("ART013", "The Death of Socrates", "Painting", "ARTIST013", "PER005", "GAL006", 1787, "Neoclassical depiction of Socrates accepting the hemlock with stoic resolve.", "/artifacts/ART013.jpg"),
    ("ART014", "Liberty Leading the People", "Painting", "ARTIST014", "PER006", "GAL006", 1830, "Allegorical celebration of the July Revolution with Marianne leading citizens.", "/artifacts/ART014.jpg"),
    ("ART015", "Bust of Nefertiti", "Sculpture", "ARTIST015", "PER001", "GAL002", -1345, "Painted limestone bust of Queen Nefertiti exemplifying Amarna period style.", "/artifacts/ART015.jpg"),
    ("ART016", "Discobolus", "Sculpture", "ARTIST016", "PER002", "GAL002", -450, "Classical Greek athlete captured mid-throw in balanced contrapposto.", "/artifacts/ART016.jpg"),
    ("ART017", "The Kiss", "Sculpture", "ARTIST001", "PER008", "GAL004", 1882, "Rodin marble of lovers embracing, originally part of The Gates of Hell.", "/artifacts/ART017.jpg"),
    ("ART018", "The Gates of Hell", "Sculpture", "ARTIST001", "PER008", "GAL004", 1880, "Monumental portal inspired by Dante featuring The Thinker and The Kiss.", "/artifacts/ART018.jpg"),
    ("ART019", "The Burghers of Calais", "Sculpture", "ARTIST001", "PER008", "GAL004", 1889, "Bronze group commemorating six citizens who offered their lives during the Hundred Years' War.", "/artifacts/ART019.jpg"),
    ("ART020", "The Last Supper", "Painting", "ARTIST002", "PER003", "GAL003", 1498, "Fresco depicting Christ announcing betrayal with dramatic perspective and gesture.", "/artifacts/ART020.jpg"),
    ("ART021", "Vitruvian Man", "Drawing", "ARTIST002", "PER003", "GAL008", 1490, "Pen and ink study correlating human proportions with geometry.", "/artifacts/ART021.jpg"),
    ("ART022", "Pieta", "Sculpture", "ARTIST003", "PER003", "GAL003", 1499, "Marble group of Mary cradling the dead Christ in restrained grief.", "/artifacts/ART022.jpg"),
    ("ART023", "Sistine Chapel Ceiling", "Painting", "ARTIST003", "PER003", "GAL003", 1512, "Vast fresco cycle including Creation of Adam and prophets.", "/artifacts/ART023.jpg"),
    ("ART024", "Sunflowers", "Painting", "ARTIST004", "PER009", "GAL005", 1888, "Still life of vibrant sunflowers in a yellow vase.", "/artifacts/ART024.jpg"),
    ("ART025", "The Potato Eaters", "Painting", "ARTIST004", "PER009", "GAL005", 1885, "Dark-toned scene of peasant family sharing a humble meal.", "/artifacts/ART025.jpg"),
    ("ART026", "Impression, Sunrise", "Painting", "ARTIST005", "PER007", "GAL005", 1872, "Harbor view whose title gave Impressionism its name.", "/artifacts/ART026.jpg"),
    ("ART027", "Les Demoiselles d'Avignon", "Painting", "ARTIST006", "PER009", "GAL007", 1907, "Proto-Cubist work with angular figures and African mask influences.", "/artifacts/ART027.jpg"),
    ("ART028", "The Old Guitarist", "Painting", "ARTIST006", "PER009", "GAL007", 1904, "Blue Period painting of a blind musician in elongated form.", "/artifacts/ART028.jpg"),
    ("ART029", "The Dance Class", "Painting", "ARTIST007", "PER007", "GAL005", 1873, "Ballet rehearsal observed by a parent in a mirror-lined studio.", "/artifacts/ART029.jpg"),
    ("ART030", "The Storm on the Sea of Galilee", "Painting", "ARTIST008", "PER004", "GAL006", 1633, "Dramatic biblical scene with disciples struggling against waves.", "/artifacts/ART030.jpg"),
    ("ART031", "The Milkmaid", "Painting", "ARTIST009", "PER004", "GAL006", 1658, "Domestic scene of a servant pouring milk in soft northern light.", "/artifacts/ART031.jpg"),
    ("ART031A", "Primavera", "Painting", "ARTIST010", "PER003", "GAL003", 1482, "Allegory of spring featuring Venus and dancing Graces in a garden.", "/artifacts/ART031A.jpg"),
    ("ART032", "Ecstasy of Saint Teresa", "Sculpture", "ARTIST012", "PER004", "GAL006", 1652, "Theatrical marble of Teresa's mystical vision in a Cornaro chapel setting.", "/artifacts/ART032.jpg"),
    ("ART033", "Napoleon Crossing the Alps", "Painting", "ARTIST013", "PER005", "GAL006", 1801, "Heroic equestrian portrait emphasizing imperial ambition.", "/artifacts/ART033.jpg"),
    ("ART034", "The Death of Marat", "Painting", "ARTIST013", "PER005", "GAL006", 1793, "Revolutionary martyr depicted in a bath after assassination.", "/artifacts/ART034.jpg"),
    ("ART035", "The Raft of the Medusa", "Painting", "ARTIST014", "PER006", "GAL006", 1819, "Romantic history painting of shipwreck survivors on a desperate raft.", "/artifacts/ART035.jpg"),
    ("ART036", "Mask of Tutankhamun", "Sculpture", "ARTIST015", "PER001", "GAL002", -1323, "Gold funerary mask of the boy pharaoh discovered in the Valley of the Kings.", "/artifacts/ART036.jpg"),
    ("ART037", "Rosetta Stone", "Sculpture", "ARTIST015", "PER001", "GAL002", -196, "Granodiorite stele key to deciphering Egyptian hieroglyphs.", "/artifacts/ART037.jpg"),
    ("ART038", "Venus de Milo", "Sculpture", "ARTIST016", "PER002", "GAL002", -130, "Hellenistic marble Aphrodite famous for missing arms and graceful S-curve.", "/artifacts/ART038.jpg"),
    ("ART039", "Laocoön and His Sons", "Sculpture", "ARTIST016", "PER002", "GAL002", -200, "Hellenistic group depicting Trojan priest and sons attacked by sea serpents.", "/artifacts/ART039.jpg"),
    ("ART040", "The Dance", "Painting", "ARTIST017", "PER009", "GAL007", 1910, "Fauvist celebration of rhythm and flat color with dancing figures.", "/artifacts/ART040.jpg"),
    ("ART041", "The Persistence of Memory", "Painting", "ARTIST018", "PER009", "GAL007", 1931, "Surrealist landscape with melting clocks in a dreamlike desert.", "/artifacts/ART041.jpg"),
    ("ART042", "The Two Fridas", "Painting", "ARTIST019", "PER010", "GAL007", 1939, "Double self-portrait exploring dual identity and heartbreak.", "/artifacts/ART042.jpg"),
    ("ART043", "Red Canna", "Painting", "ARTIST020", "PER010", "GAL007", 1924, "Enlarged flower study blending abstraction and botanical detail.", "/artifacts/ART043.jpg"),
    ("ART044", "Black Iris III", "Painting", "ARTIST020", "PER010", "GAL007", 1926, "Close-up iris composition exploring sensuality and form.", "/artifacts/ART044.jpg"),
    ("ART045", "Bal du moulin de la Galette", "Painting", "ARTIST005", "PER007", "GAL005", 1876, "Outdoor scene of Parisians dancing at a Montmartre gathering.", "/artifacts/ART045.jpg"),
    ("ART046", "The Scream", "Painting", "ARTIST004", "PER009", "GAL005", 1893, "Expressionist icon of anxiety against a blood-red sky (study version held in companion collection).", "/artifacts/ART046.jpg"),
    ("ART047", "Woman with a Parasol", "Painting", "ARTIST005", "PER007", "GAL005", 1875, "Sunlit portrait of Monet's wife and son on a breezy hillside.", "/artifacts/ART047.jpg"),
    ("ART048", "The Card Players", "Painting", "ARTIST004", "PER009", "GAL005", 1895, "Post-Impressionist study of Provençal peasants absorbed in a card game.", "/artifacts/ART048.jpg"),
    ("ART049", "The Age of Bronze", "Sculpture", "ARTIST001", "PER008", "GAL004", 1877, "Life-size male nude that established Rodin's reputation for realism.", "/artifacts/ART049.jpg"),
    ("ART050", "Man with Broken Nose", "Sculpture", "ARTIST001", "PER008", "GAL004", 1864, "Early bust demonstrating Rodin's interest in character and surface texture.", "/artifacts/ART050.jpg"),
    ("ART051", "The Winged Victory of Samothrace", "Sculpture", "ARTIST016", "PER002", "GAL002", -190, "Hellenistic Nike figure poised on a ship's prow with dramatic drapery.", "/artifacts/ART051.jpg"),
    ("ART052", "Great Sphinx of Giza", "Sculpture", "ARTIST015", "PER001", "GAL002", -2500, "Colossal limestone guardian with a lion body and human head.", "/artifacts/ART052.jpg"),
    ("ART053", "The School of Athens", "Painting", "ARTIST002", "PER003", "GAL003", 1511, "Fresco gathering ancient philosophers in an idealized architectural space.", "/artifacts/ART053.jpg"),
    ("ART054", "The Arnolfini Portrait", "Painting", "ARTIST009", "PER004", "GAL006", 1434, "Detailed double portrait rich with symbolic domestic objects.", "/artifacts/ART054.jpg"),
    ("ART055", "The Creation of Adam", "Painting", "ARTIST003", "PER003", "GAL003", 1512, "Central Sistine panel depicting God reaching toward Adam.", "/artifacts/ART055.jpg"),
    ("ART056", "Campbell's Soup Cans", "Painting", "ARTIST006", "PER010", "GAL007", 1962, "Pop Art serial imagery elevating commercial design to fine art.", "/artifacts/ART056.jpg"),
    ("ART057", "The Harvesters", "Painting", "ARTIST008", "PER004", "GAL006", 1565, "Landscape with peasants resting during harvest season (companion to Flemish masters).", "/artifacts/ART057.jpg"),
    ("ART058", "The Third of May 1808", "Painting", "ARTIST006", "PER009", "GAL007", 1814, "Goya-influenced anti-war scene of Spanish resistance (Picasso study collection).", "/artifacts/ART058.jpg"),
    ("ART059", "Bronze Statue of Marcus Aurelius", "Sculpture", "ARTIST016", "PER002", "GAL002", 175, "Equestrian portrait of the stoic emperor, rare surviving Roman bronze.", "/artifacts/ART059.jpg"),
    ("ART060", "Terracotta Army Warrior", "Sculpture", "ARTIST015", "PER001", "GAL002", -210, "Life-sized clay soldier from Emperor Qin's mausoleum complex (cultural exchange exhibit).", "/artifacts/ART060.jpg"),
]

ARTIFACT_EXHIBITIONS = [
    ("ART001", "EXH001"), ("ART017", "EXH001"), ("ART018", "EXH001"), ("ART019", "EXH001"), ("ART049", "EXH001"),
    ("ART004", "EXH002"), ("ART005", "EXH002"), ("ART026", "EXH002"), ("ART045", "EXH002"), ("ART047", "EXH002"),
    ("ART002", "EXH003"), ("ART003", "EXH003"), ("ART010", "EXH003"), ("ART020", "EXH003"), ("ART053", "EXH003"),
    ("ART015", "EXH004"), ("ART036", "EXH004"), ("ART038", "EXH004"), ("ART051", "EXH004"), ("ART052", "EXH004"),
    ("ART006", "EXH005"), ("ART027", "EXH005"), ("ART041", "EXH005"), ("ART042", "EXH005"), ("ART056", "EXH005"),
]


def _write_documents(conn: sqlite3.Connection) -> None:
    """Generate document corpus with multi-chunk segmentation and rich source metadata."""
    docs_dir = DOCUMENTS_DIR
    for sub in ["artifact_catalogues", "artist_biographies", "historical_documents", "exhibition_guides", "museum_brochures"]:
        (docs_dir / sub).mkdir(parents=True, exist_ok=True)

    cursor = conn.cursor()
    doc_idx = 0
    chunk_idx = 0

    # Artifact catalogues (3 chunks per artifact)
    for art in ARTIFACTS:
        artifact_id, name = art[0], art[1]
        artist_id = art[3]
        period_id = art[4]
        year = art[6]
        desc = art[7]
        doc_id = f"DOC{doc_idx:04d}"
        doc_idx += 1
        path = docs_dir / "artifact_catalogues" / f"{artifact_id}.txt"

        chunk_texts = [
            f"Catalogue Entry Overview: {name}. {name} is a renowned masterwork created in {year}. {desc} It stands as one of the hallmark acquisitions in our museum collection.",
            f"Curatorial & Technical Analysis of {name}: Created around {year}, the piece showcases distinctive artistic techniques characteristic of its period. Scholars note its composition, light quality, and surface treatment as central to its aesthetic power.",
            f"Provenance & Exhibition History of {name}: {name} has been featured in major international retrospectives and museum displays. Located within our collection galleries, it remains a subject of active research and public admiration."
        ]

        full_doc = "\n\n".join(chunk_texts)
        path.write_text(full_doc, encoding="utf-8")

        cursor.execute(
            "INSERT INTO documents (document_id, title, source_type, source_path, artifact_id, artist_id, period_id) VALUES (?,?,?,?,?,?,?)",
            (doc_id, f"Catalogue: {name}", "artifact_catalogue", str(path.relative_to(DATASET_DIR)), artifact_id, artist_id, period_id),
        )

        for c_i, c_text in enumerate(chunk_texts):
            meta = {
                "title": f"Catalogue: {name}",
                "source_type": "artifact_catalogue",
                "artifact_id": artifact_id,
                "artist_id": artist_id,
                "period_id": period_id,
                "section": f"Section {c_i + 1}",
                "page": c_i + 1
            }
            cursor.execute(
                "INSERT INTO document_chunks (chunk_id, document_id, chunk_index, text, metadata_json) VALUES (?,?,?,?,?)",
                (f"CHUNK{chunk_idx:05d}", doc_id, c_i, c_text, json.dumps(meta)),
            )
            chunk_idx += 1

    # Artist biographies (3 chunks per artist)
    for artist in ARTISTS:
        artist_id, name, birth, death, nationality, bio = artist
        doc_id = f"DOC{doc_idx:04d}"
        doc_idx += 1
        path = docs_dir / "artist_biographies" / f"{artist_id}.txt"

        chunk_texts = [
            f"Artist Biography - Early Life & Background: {name} ({birth}–{death}) was a prominent {nationality} master. {bio}",
            f"Artistic Legacy & Innovations of {name}: Throughout their prolific career, {name} revolutionized techniques, influencing contemporaries and generations of artists.",
            f"Museum Holdings & Critical Reception: Our museum proudly preserves seminal creations by {name}. Scholars praise {name}'s profound impact on modern art history."
        ]

        full_doc = "\n\n".join(chunk_texts)
        path.write_text(full_doc, encoding="utf-8")

        cursor.execute(
            "INSERT INTO documents (document_id, title, source_type, source_path, artifact_id, artist_id, period_id) VALUES (?,?,?,?,?,?,?)",
            (doc_id, f"Biography: {name}", "artist_biography", str(path.relative_to(DATASET_DIR)), None, artist_id, None),
        )

        for c_i, c_text in enumerate(chunk_texts):
            meta = {
                "title": f"Biography: {name}",
                "source_type": "artist_biography",
                "artist_id": artist_id,
                "section": f"Biographical Section {c_i + 1}",
                "page": c_i + 1
            }
            cursor.execute(
                "INSERT INTO document_chunks (chunk_id, document_id, chunk_index, text, metadata_json) VALUES (?,?,?,?,?)",
                (f"CHUNK{chunk_idx:05d}", doc_id, c_i, c_text, json.dumps(meta)),
            )
            chunk_idx += 1

    # Historical documents per period (2 chunks per period)
    for period in PERIODS:
        period_id, name, start, end, desc = period
        doc_id = f"DOC{doc_idx:04d}"
        doc_idx += 1
        path = docs_dir / "historical_documents" / f"{period_id}.txt"

        chunk_texts = [
            f"Historical Context: {name} Movement ({start} to {end}). {desc}",
            f"Cultural Impact of {name}: Works created during the {name} era reflect major societal transformations, technological advances, and philosophical shifts."
        ]

        full_doc = "\n\n".join(chunk_texts)
        path.write_text(full_doc, encoding="utf-8")

        cursor.execute(
            "INSERT INTO documents (document_id, title, source_type, source_path, artifact_id, artist_id, period_id) VALUES (?,?,?,?,?,?,?)",
            (doc_id, f"History: {name}", "historical_document", str(path.relative_to(DATASET_DIR)), None, None, period_id),
        )

        for c_i, c_text in enumerate(chunk_texts):
            meta = {
                "title": f"History: {name}",
                "source_type": "historical_document",
                "period_id": period_id,
                "section": f"History Section {c_i + 1}",
                "page": c_i + 1
            }
            cursor.execute(
                "INSERT INTO document_chunks (chunk_id, document_id, chunk_index, text, metadata_json) VALUES (?,?,?,?,?)",
                (f"CHUNK{chunk_idx:05d}", doc_id, c_i, c_text, json.dumps(meta)),
            )
            chunk_idx += 1

    # Exhibition guides (2 chunks per exhibition)
    for exh in EXHIBITIONS:
        exh_id, name, start, end, desc = exh
        doc_id = f"DOC{doc_idx:04d}"
        doc_idx += 1
        path = docs_dir / "exhibition_guides" / f"{exh_id}.txt"

        chunk_texts = [
            f"Exhibition Overview: {name}. Scheduled from {start} to {end}. {desc}",
            f"Curatorial Highlights: Visitors to '{name}' will experience thematic pairings, archival documents, and interactive digital displays."
        ]

        full_doc = "\n\n".join(chunk_texts)
        path.write_text(full_doc, encoding="utf-8")

        cursor.execute(
            "INSERT INTO documents (document_id, title, source_type, source_path, artifact_id, artist_id, period_id) VALUES (?,?,?,?,?,?,?)",
            (doc_id, f"Exhibition: {name}", "exhibition_guide", str(path.relative_to(DATASET_DIR)), None, None, None),
        )

        for c_i, c_text in enumerate(chunk_texts):
            meta = {
                "title": f"Exhibition: {name}",
                "source_type": "exhibition_guide",
                "exhibition_id": exh_id,
                "section": f"Guide Section {c_i + 1}",
                "page": c_i + 1
            }
            cursor.execute(
                "INSERT INTO document_chunks (chunk_id, document_id, chunk_index, text, metadata_json) VALUES (?,?,?,?,?)",
                (f"CHUNK{chunk_idx:05d}", doc_id, c_i, c_text, json.dumps(meta)),
            )
            chunk_idx += 1

    # Museum brochure (2 chunks)
    doc_id = f"DOC{doc_idx:04d}"
    path = docs_dir / "museum_brochures" / "welcome.txt"
    chunk_texts = [
        "Welcome to the Digital AI Museum Guide. Our curated collection spans ancient civilizations, Renaissance masterworks, Impressionist masterpieces, and modern sculptures.",
        "Exploring with AI Guide: Visitors can upload photos of museum pieces for visual recognition, query historical facts, and explore curated exhibitions grounded in peer-reviewed museum archives."
    ]
    full_doc = "\n\n".join(chunk_texts)
    path.write_text(full_doc, encoding="utf-8")

    cursor.execute(
        "INSERT INTO documents (document_id, title, source_type, source_path, artifact_id, artist_id, period_id) VALUES (?,?,?,?,?,?,?)",
        (doc_id, "Museum Welcome Brochure", "museum_brochure", str(path.relative_to(DATASET_DIR)), None, None, None),
    )

    for c_i, c_text in enumerate(chunk_texts):
        meta = {"title": "Museum Welcome Brochure", "source_type": "museum_brochure", "section": f"Brochure Section {c_i + 1}"}
        cursor.execute(
            "INSERT INTO document_chunks (chunk_id, document_id, chunk_index, text, metadata_json) VALUES (?,?,?,?,?)",
            (f"CHUNK{chunk_idx:05d}", doc_id, c_i, c_text, json.dumps(meta)),
        )
        chunk_idx += 1


def seed() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()
    conn = get_connection()
    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO historical_periods VALUES (?,?,?,?,?)", PERIODS
    )
    cur.executemany("INSERT INTO artists VALUES (?,?,?,?,?,?)", ARTISTS)
    cur.executemany("INSERT INTO galleries VALUES (?,?,?,?,?)", GALLERIES)
    cur.executemany("INSERT INTO exhibitions VALUES (?,?,?,?,?)", EXHIBITIONS)
    cur.executemany(
        "INSERT INTO artifacts (artifact_id,name,type,artist_id,period_id,gallery_id,year,description,image_path) VALUES (?,?,?,?,?,?,?,?,?)",
        ARTIFACTS,
    )
    cur.executemany("INSERT INTO artifact_exhibitions VALUES (?,?)", ARTIFACT_EXHIBITIONS)
    _write_documents(conn)
    conn.commit()
    conn.close()
    print(f"Seeded database at {DB_PATH}")
    print(f"  Artifacts: {len(ARTIFACTS)}")
    print(f"  Artists: {len(ARTISTS)}")
    print(f"  Periods: {len(PERIODS)}")
    print(f"  Galleries: {len(GALLERIES)}")
    print(f"  Exhibitions: {len(EXHIBITIONS)}")


if __name__ == "__main__":
    seed()
