import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# =========================
# CONFIGURATION
# =========================

USERNAME = "RVKDPod"  # <-- Your GitHub username
REPO = "personal-podcasts"

SHOWS = {
    "jre": {
        "title": "Joe Rogan Experience (Private)",
        "desc": "Private JRE archive",
        "art": "artwork/jre.jpg"
    },
    "sam-hyde": {
        "title": "Sam Hyde (Private)",
        "desc": "Private Sam Hyde archive",
        "art": "artwork/sam-hyde.jpg"
    },
    "misc": {
        "title": "Misc Pods (Private)",
        "desc": "Private Misc Pods archive",
        "art": "artwork/misc.jpg"
    }
}

# =========================
# FUNCTION TO GENERATE A FEED
# =========================

def generate_feed(show):
    print(f"\nGenerating feed for: {show}")
    
    os.makedirs("feeds", exist_ok=True)

    # RSS root with iTunes namespace
    rss = Element("rss", version="2.0", attrib={
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"
    })
    channel = SubElement(rss, "channel")

    # Channel metadata
    SubElement(channel, "title").text = SHOWS[show]["title"]
    SubElement(channel, "link").text = f"https://{USERNAME}.github.io/{REPO}/feeds/{show}.xml"
    SubElement(channel, "description").text = SHOWS[show]["desc"]
    SubElement(channel, "itunes:image", href=f"https://{USERNAME}.github.io/{REPO}/{SHOWS[show]['art']}")

    mp3_path = os.path.join("mp3", show)
    if not os.path.exists(mp3_path):
        print(f"Warning: folder not found: {mp3_path}")
        files = []
    else:
        # Include both MP3 and M4A
        files = sorted(f for f in os.listdir(mp3_path) if f.lower().endswith((".mp3", ".m4a")))

    if not files:
        print(f"No audio files found for {show} in {mp3_path}")
    else:
        print(f"Found {len(files)} audio file(s) for {show}: {files}")

    for f in files:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = f.replace(".mp3", "").replace(".m4a", "")
        
        # Set MIME type based on extension
        if f.lower().endswith(".mp3"):
            mime = "audio/mpeg"
        elif f.lower().endswith(".m4a"):
            mime = "audio/mp4"
        else:
            mime = "application/octet-stream"

        SubElement(item, "enclosure",
                   url=f"https://{USERNAME}.github.io/{REPO}/{mp3_path.replace(os.sep, '/')}/{f}",
                   type=mime)
        SubElement(item, "guid").text = f"{show}-{f}"

    xml_str = minidom.parseString(tostring(rss)).toprettyxml(indent="  ")
    output_file = os.path.join("feeds", f"{show}.xml")
    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write(xml_str)
    print(f"Feed generated: {output_file}")

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    for show in SHOWS:
        generate_feed(show)
    print("\nAll feeds generated successfully!")

