import re
import os
import hashlib
import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.dom import minidom

# =====================
# CONFIG — EDIT THESE
# =====================
USERNAME = "RVKDPod"
REPO = "personal-podcasts"
BASE_URL = f"https://{USERNAME}.github.io/{REPO}"

MP3_ROOT = "mp3"
FEED_ROOT = "feeds"
DEFAULT_ARTWORK = f"{BASE_URL}/artwork/default.jpg"

AUDIO_EXTENSIONS = (".mp3", ".m4a")

# =====================
# HELPERS
# =====================

def pretty_xml(elem):
    rough = ElementTree(elem).write("temp.xml", encoding="utf-8", xml_declaration=True)
    with open("temp.xml", "rb") as f:
        reparsed = minidom.parse(f)
    os.remove("temp.xml")
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")

def stable_guid(show, filename, size):
    base = f"{show}-{filename}-{size}"
    return hashlib.md5(base.encode("utf-8")).hexdigest()

def guess_mime(filename):
    if filename.lower().endswith(".mp3"):
        return "audio/mpeg"
    if filename.lower().endswith(".m4a"):
        return "audio/mp4"
    return "application/octet-stream"

def human_title(filename):
    name = os.path.splitext(filename)[0]
    return name.replace("_", " ").replace("-", " ").strip()

# =====================
# MAIN FEED GENERATOR
# =====================

def generate_feed(show):
    show_path = os.path.join(MP3_ROOT, show)
    feed_path = os.path.join(FEED_ROOT, f"{show}.xml")

    audio_files = sorted(
        f for f in os.listdir(show_path)
        if f.lower().endswith(AUDIO_EXTENSIONS)
    )

    if not audio_files:
        print(f"No audio files found for {show}")
        return

    rss = Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"
    })

    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = show
    SubElement(channel, "link").text = BASE_URL
    SubElement(channel, "language").text = "en-us"
    SubElement(channel, "description").text = f"Private podcast feed for {show}"
    SubElement(channel, "itunes:explicit").text = "no"

    artwork_url = f"{BASE_URL}/artwork/{show}.jpg"
    SubElement(channel, "itunes:image", href=artwork_url)

    now = datetime.datetime.utcnow()

    for idx, filename in enumerate(audio_files, start=1):
        file_path = os.path.join(show_path, filename)
	file_size = os.path.getsize(file_path)
	mime = guess_mime(filename)

	item = SubElement(channel, "item")

	title = human_title(filename)
	SubElement(item, "title").text = title
	SubElement(item, "itunes:title").text = title
	SubElement(item, "itunes:episode").text = str(idx)

	description = load_description(show_path, filename)

	SubElement(item, "description").text = description
	SubElement(item, "itunes:summary").text = description
	SubElement(item, "itunes:subtitle").text = description[:255]

	guid_value = stable_guid(show, filename, file_size)
	guid_el = SubElement(item, "guid")
	guid_el.text = guid_value
	guid_el.set("isPermaLink", "false")

	pub_date = extract_date(filename, file_path)
	SubElement(item, "pubDate").text = pub_date.strftime(
	    "%a, %d %b %Y %H:%M:%S GMT"
	)

	enclosure_url = f"{BASE_URL}/{show_path.replace(os.sep, '/')}/{filename}"

	SubElement(
    	    item,
    	    "enclosure",
    	    url=enclosure_url,
    	    length=str(file_size),
    	    type=mime
	)

    xml_bytes = pretty_xml(rss)

    with open(feed_path, "wb") as f:
        f.write(xml_bytes)

    print(f"Feed generated: {feed_path}")

# =====================
# ENTRY POINT
# =====================

if __name__ == "__main__":
    os.makedirs(FEED_ROOT, exist_ok=True)

    for show in os.listdir(MP3_ROOT):
        show_path = os.path.join(MP3_ROOT, show)
        if os.path.isdir(show_path):
            print(f"Generating feed for: {show}")
            generate_feed(show)

    print("\nAll feeds generated successfully!")


