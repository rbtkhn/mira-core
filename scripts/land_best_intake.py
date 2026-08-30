from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import SimpleNamespace

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import voice_indexes

REPO_ROOT = Path(__file__).resolve().parent.parent
NG_ROOT = REPO_ROOT / "narrative-geopolitics"
ARCHIVE_ROOT = NG_ROOT.parent / "archive" / "sources" / "geopolitics"
MANIFEST_PATH = ARCHIVE_ROOT / "source-manifest.json"
ARCHIVE_SOURCES_ROOT = ARCHIVE_ROOT / "sources"
METADATA_SUFFIXES = (".txt", ".md")
REPEATABLE_FIELDS = {"voice_slug", "host_people", "guest_people"}
TRIM_FIELD_ORDER = (
    "opening_trim_applied",
    "opening_trim_rule",
    "opening_trim_chars_saved",
    "opening_trim_words_saved",
    "closing_trim_applied",
    "closing_trim_rule",
    "closing_trim_chars_saved",
    "closing_trim_words_saved",
)
SECTIONING_FIELD_ORDER = (
    "transcript_curation",
    "section_count",
    "section_pass",
)
ASR_FIELD_ORDER = (
    "asr_repair_applied",
    "asr_repair_pass",
)
PROCESSING_FIELD_ORDER = (
    "asr_disposition",
    "speaker_attribution",
    "speaker_attribution_reason",
    "sectioning_disposition",
    "sectioning_reason",
    "quotation_readiness",
    "quotation_readiness_reason",
)
SECTIONING_APPROVED_HOSTS = {
    "alexander-mercouris",
    "daniel-davis",
    "dialogue-works",
    "glenn-diesen",
    "judging-freedom",
    "mario-nawfal",
    "moral-resistance",
    "reason-resist",
}
ASR_REPAIR_APPROVED_HOSTS = {
    "alexander-mercouris",
    "daniel-davis",
    "dialogue-works",
    "glenn-diesen",
    "judging-freedom",
    "mario-nawfal",
    "moral-resistance",
    "reason-resist",
}
SECTIONING_PASS_LABEL = "2026-07-09 semantic-section-v1"


def safe_int(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0
ASR_REPAIR_PASS_LABEL = "2026-07-09 asr-repair-v1"
TOPIC_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "for",
    "from",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "so",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "we",
    "what",
    "when",
    "where",
    "which",
    "with",
    "you",
}
TOPIC_FILLER_WORDS = {
    "about",
    "actually",
    "again",
    "all",
    "also",
    "another",
    "any",
    "big",
    "because",
    "been",
    "being",
    "can't",
    "came",
    "cant",
    "come",
    "course",
    "could",
    "did",
    "even",
    "every",
    "feel",
    "finish",
    "folks",
    "get",
    "going",
    "got",
    "had",
    "hear",
    "have",
    "huge",
    "i'm",
    "im",
    "into",
    "it's",
    "just",
    "know",
    "like",
    "look",
    "made",
    "make",
    "many",
    "more",
    "most",
    "much",
    "need",
    "nothing",
    "not",
    "now",
    "off",
    "only",
    "other",
    "our",
    "out",
    "over",
    "people",
    "plain",
    "point",
    "president",
    "questions",
    "really",
    "right",
    "said",
    "saying",
    "see",
    "showing",
    "something",
    "sort",
    "still",
    "such",
    "take",
    "tell",
    "than",
    "them",
    "then",
    "there's",
    "thing",
    "think",
    "these",
    "through",
    "today",
    "told",
    "trying",
    "very",
    "want",
    "went",
    "well",
    "were",
    "would",
    "what's",
    "why",
    "yeah",
    "yes",
}
DOMAIN_TOPIC_PHRASES = (
    "american people",
    "blackmail",
    "white house",
    "middle east",
    "west bank",
    "east jerusalem",
    "international law",
    "free world",
    "third party movement",
    "new republic",
    "oil prices",
    "oil markets",
    "gas prices",
    "interest rates",
    "rare earth",
    "fertilizer",
    "nuclear power",
    "silicon valley",
    "nuclear weapon",
    "nuclear weapons",
    "ceasefire",
    "hezbollah",
    "hormuz",
    "lebanon",
    "missile cities",
    "missile factories",
    "mountain ranges",
    "strategic petroleum reserve",
    "iran",
    "irgc",
    "israel",
    "trump",
    "netanyahu",
    "turkey",
    "syria",
    "russia",
    "ukraine",
    "gaza",
    "palestinian",
    "palestine",
    "europe",
    "european union",
    "united nations",
    "international court",
    "jcpoa",
    "pentagon",
    "treasury",
    "economy",
    "energy markets",
    "shipping lane",
    "shipping lanes",
)
UPPERCASE_TOPIC_TOKENS = {"AI", "CIA", "EU", "IAEA", "IDF", "JCPOA", "NATO", "PLO", "UN", "US"}
GLOBAL_ASR_REPAIRS: tuple[tuple[str, str], ...] = (
    (r"(?m)^Transcripts:\s*\n?", ""),
    (r"\bAnchora\b", "Ankara"),
    (r"\btheou\b", "MOU"),
    (r"\bfullcale\b", "full-scale"),
    (r"\bupgraded ed\b", "upgraded"),
    (r"\boff-the cuff\b", "off-the-cuff"),
    (r"\bdouble cross\b", "double-cross"),
    (r"\bstraight of Horm(?:ones|ones|os)\b", "Strait of Hormuz"),
    (r"\bstraight of hormones\b", "Strait of Hormuz"),
    (r"\bstraight of hormos\b", "Strait of Hormuz"),
    (r"\bstraight of hamoos\b", "Strait of Hormuz"),
    (r"\bstraight of Hermoose\b", "Strait of Hormuz"),
    (r"\bstraight of foremost\b", "Strait of Hormuz"),
    (r"\bstraight of formos\b", "Strait of Hormuz"),
    (r"\bstraight of moose\b", "Strait of Hormuz"),
    (r"\bthe state of Hormuz\b", "the Strait of Hormuz"),
    (r"\bwhich were was supposed to be\b", "which was supposed to be"),
)
HOST_ASR_REPAIRS: dict[str, tuple[tuple[str, str], ...]] = {
    "daniel-davis": (
        (r"\bROG, uh struck them\b", "Iran struck them"),
        (r"\bdefinite inde definite incumbrances\b", "definite encumbrances"),
    ),
    "mario-nawfal": (
        (
            r"want breathing space before they continue their operation to capture car guy into whatever do you think you know this argument is gaining more weight ",
            "",
        ),
        (r"\bthe he rug pulls\b", "he rug-pulls"),
        (r"\bcapture Khagan and whatever\b", "capture Kharg Island or whatever"),
    ),
    "dialogue-works": (
        (
            r"\bfor the first time, they agree on that mou is over here is what\b",
            "for the first time, they agree that the MOU is over. ",
        ),
    ),
    "reason-resist": (
        (r"\bDemetri Lcer(?:is|as)\b", "Dimitri Lascaris"),
        (r"\bDimmitri\b", "Dimitri"),
        (r"\bDmitri\b", "Dimitri"),
        (r"\battackums\b", "ATACMS"),
        (r"\battacker missiles\b", "ATACMS missiles"),
        (r"\bAndre Mariano\b", "Andrei Martyanov"),
        (r"\bBarakta\b", "Bayraktar"),
        (r"\bGata\b", "Qatar"),
        (r"\bGalani\b", "al-Jolani"),
        (r"\bTartis\b", "Tartus"),
        (r"\bKmium\b", "Khmeimim"),
        (r"\bErdawan\b", "Erdogan"),
        (r"\bBoserus\b", "Bosporus"),
        (r"\bmantra treaty\b", "Montreux Convention"),
        (r"\bHakan Fedan\b", "Hakan Fidan"),
        (r"\bAnton Czechov\b", "Anton Chekhov"),
        (r"\bSkullan Island\b", "Sakhalin Island"),
        (r"\bJohn Radcliffe\b", "John Ratcliffe"),
        (r"\b(?:Radkut|Ratiff|Rakov)\b", "Ratcliffe"),
        (r"\bNarishkin\b", "Naryshkin"),
        (r"\bKarakas\b", "Caracas"),
        (r"\bMadura\b", "Maduro"),
        (r"\bDeli Rodriguez\b", "Delcy Rodriguez"),
        (r"\bRiyad\b", "Riyadh"),
        (r"\bLavro Rob\b", "Lavrov"),
        (r"\bMario Rubio\b", "Marco Rubio"),
    ),
}


@dataclass(frozen=True)
class HostTrimRule:
    slug: str
    label: str
    opening_markers: tuple[str, ...] = ()
    opening_snippets: tuple[str, ...] = ()
    opening_regexes: tuple[str, ...] = ()
    closing_markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class HostProfile:
    slug: str
    aliases: tuple[str, ...]
    host_name: str
    host_people: tuple[str, ...]
    channel_name: str
    show_title: str
    show: str
    default_voice_slug: str | None = None
    default_source_form: str = "interview"


@dataclass(frozen=True)
class LandingPlan:
    source_path: Path
    source_text: str
    manifest_row: dict[str, object]


HOST_TRIM_RULES: dict[str, HostTrimRule] = {
    "mario-nawfal": HostTrimRule(
        slug="mario-nawfal",
        label="mario-nawfal-v1",
        opening_markers=(
            "So just to kind of recap for the audience",
            "Well, the reality that we're dealing with now is",
            "The issue as I told you before",
            "What we know right now is",
            "The big issue right now is",
            "To kind of recap for the audience",
        ),
        closing_markers=(
            ">> Bye-bye. All right, guys.",
            ">> Bye-bye. >> Bye-bye. All right, guys.",
            "All right, guys. I'll be going live again",
            "Thanks everyone.",
        ),
    ),
    "daniel-davis": HostTrimRule(
        slug="daniel-davis",
        label="daniel-davis-closing-v1",
        closing_markers=(
            "And uh we will be back in about 1 hour.",
            "You know we don't have sponsors cuz we hate to hit you over the head with ads.",
            "And we'll see you this afternoon at I believe 2 o'clock.",
            "We'll see you then at 2 o'clock on the Daniel Davis deep dive.",
            "We'll see you on the next episode of the Daniel Davis deep dive.",
            "You know, I don't try to talk you into buying gold or tell you how to run your stock portfolio, but there is a way you can help us.",
            "That's all I got for you folks right now.",
        ),
    ),
    "alexander-mercouris": HostTrimRule(
        slug="alexander-mercouris",
        label="alexander-mercouris-v1",
        opening_snippets=(
            "And before I proceed with this program, let me remind you again to tick the like button and to check your subscription to this channel.",
            "And before I proceed with this program, let me remind you again to tick the like button and check your subscription to this channel.",
            "And before I proceed with this program, let me remind you to tick the like button and to check your subscription to this channel.",
            "And before I proceed with this program, let me remind you to tick the like button and check your subscription to this channel.",
        ),
        closing_markers=(
            "\n### Close",
            "Anyway, this is where I'm going to finish today's program.",
            "Anyway, this is where I am going to finish today's program.",
            "But in the meantime, this is where I'm going to finish today's program.",
            "Let me remind you again, you can find all our programs on our various platforms",
            "Let me remind you that you can find all our programs on our various platforms",
        ),
    ),
    "dialogue-works": HostTrimRule(
        slug="dialogue-works",
        label="dialogue-works-wrapper-v1",
        opening_regexes=(
            r"^[^\n]+ - YouTube\s*\n\s*Transcripts:\s*\n+",
        ),
    ),
    "moral-resistance": HostTrimRule(
        slug="moral-resistance",
        label="moral-resistance-wrapper-v1",
        opening_regexes=(
            r"^[^\n]+ - YouTube\s*\n\s*Transcripts:\s*\n+",
        ),
    ),
}

HOST_PROFILES: dict[str, HostProfile] = {
    "alexander-mercouris": HostProfile(
        slug="alexander-mercouris",
        aliases=("alexander mercouris", "mercouris"),
        host_name="Alexander Mercouris",
        host_people=("Alexander Mercouris",),
        channel_name="Alexander Mercouris",
        show_title="Mercouris",
        show="Mercouris",
        default_voice_slug="mercouris",
        default_source_form="solo",
    ),
    "daniel-davis": HostProfile(
        slug="daniel-davis",
        aliases=("daniel davis", "lt col daniel davis", "daniel davis deep dive"),
        host_name="Lt. Col. Daniel Davis",
        host_people=("Lt. Col. Daniel Davis",),
        channel_name="Daniel Davis Deep Dive",
        show_title="Daniel Davis Deep Dive",
        show="Daniel Davis Deep Dive",
        default_voice_slug="davis",
        default_source_form="interview",
    ),
    "dialogue-works": HostProfile(
        slug="dialogue-works",
        aliases=("dialogue works", "nima alkhorshid", "nima"),
        host_name="Nima Alkhorshid",
        host_people=("Nima Alkhorshid",),
        channel_name="Dialogue Works",
        show_title="Dialogue Works",
        show="Dialogue Works",
        default_source_form="interview",
    ),
    "glenn-diesen": HostProfile(
        slug="glenn-diesen",
        aliases=("glenn diesen", "glenn"),
        host_name="Glenn Diesen",
        host_people=("Glenn Diesen",),
        channel_name="Glenn Diesen",
        show_title="Glenn Diesen",
        show="Glenn Diesen",
        default_voice_slug="diesen",
        default_source_form="interview",
    ),
    "judging-freedom": HostProfile(
        slug="judging-freedom",
        aliases=("judging freedom", "judge napolitano", "andrew napolitano"),
        host_name="Judge Andrew Napolitano",
        host_people=("Judge Andrew Napolitano",),
        channel_name="Judging Freedom",
        show_title="Judging Freedom",
        show="Judging Freedom",
        default_source_form="interview",
    ),
    "mario-nawfal": HostProfile(
        slug="mario-nawfal",
        aliases=("mario nawfal", "the roundtable show", "roundtable show"),
        host_name="Mario Nawfal",
        host_people=("Mario Nawfal",),
        channel_name="Mario Nawfal",
        show_title="The Roundtable Show",
        show="The Roundtable Show",
        default_source_form="interview",
    ),
    "moral-resistance": HostProfile(
        slug="moral-resistance",
        aliases=("moral resistance", "sulaiman ahmed"),
        host_name="Sulaiman Ahmed",
        host_people=("Sulaiman Ahmed",),
        channel_name="Moral Resistance",
        show_title="Moral Resistance",
        show="Moral Resistance",
        default_source_form="interview",
    ),
    "neutrality-studies": HostProfile(
        slug="neutrality-studies",
        aliases=("neutrality studies", "pascal lottaz"),
        host_name="Pascal Lottaz",
        host_people=("Pascal Lottaz",),
        channel_name="Neutrality Studies",
        show_title="Neutrality Studies",
        show="Neutrality Studies",
        default_source_form="interview",
    ),
}

HOST_CUE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\byou know,\s*glenn\b", "glenn-diesen"),
    (r"\bglenn,\s+the bottom line here\b", "glenn-diesen"),
    (r"\band we are live\b", "moral-resistance"),
    (r"\bhi everybody\b", "dialogue-works"),
    (r"\bwelcome back to neutrality studies\b", "neutrality-studies"),
)

VOICE_HINTS: tuple[tuple[str, str, str], ...] = (
    ("alastair crooke", "crooke", "Alastair Crooke"),
    ("andrei martyanov", "martyanov", "Andrei Martyanov"),
    ("anthony aguilar", "aguilar", "Lt. Col. Anthony Aguilar"),
    ("col douglas macgregor", "macgregor", "Douglas Macgregor"),
    ("douglas macgregor", "macgregor", "Douglas Macgregor"),
    ("daniel davis", "davis", "Lt. Col. Daniel Davis"),
    ("jeffrey sachs", "sachs", "Jeffrey Sachs"),
    ("john helmer", "helmer", "John Helmer"),
    ("john mearsheimer", "mearsheimer", "John Mearsheimer"),
    ("larry johnson", "johnson", "Larry Johnson"),
    ("max blumenthal", "blumenthal", "Max Blumenthal"),
    ("matthew hoh", "hoh", "Matthew Hoh"),
    ("prof. s. m. marandi", "marandi", "Seyed Mohammad Marandi"),
    ("prof s. m. marandi", "marandi", "Seyed Mohammad Marandi"),
    ("robert barnes", "barnes", "Robert Barnes"),
    ("robert pape", "pape", "Prof. Robert Pape"),
    ("scott ritter", "ritter", "Scott Ritter"),
    ("pepe escobar", "escobar", "Pepe Escobar"),
    ("trita parsi", "parsi", "Trita Parsi"),
    ("seyed m. marandi", "marandi", "Seyed Mohammad Marandi"),
    ("seyed mohammad marandi", "marandi", "Seyed Mohammad Marandi"),
    ("stanislav krapivnik", "krapivnik", "Stanislav Krapivnik"),
    ("steve jermy", "jermy", "Steve Jermy"),
)


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_frontmatter(args: SimpleNamespace, title_slug: str, body: str) -> str:
    host_slug = getattr(args, "host_slug", "") or ""
    asr_repair_applied = bool(getattr(args, "asr_repair_applied", False))
    asr_repair_pass = getattr(args, "asr_repair_pass", "") or ""
    asr_disposition = "repaired" if asr_repair_applied else "needs-repair"
    turn_marker_count = len(re.findall(r"(?m)^>> ", body))
    speaker_attribution = "turn-labeled" if turn_marker_count >= 2 else "unknown"
    speaker_attribution_reason = (
        "Source transcript preserves explicit turn boundaries; identities are not assigned where the source does not establish them."
        if speaker_attribution == "turn-labeled"
        else "Source-level host and guest metadata does not establish transcript turn attribution."
    )
    sectioning_disposition = (
        "sectioned" if args.transcript_curation == "curated_sectioned" else "preserved-unsectioned"
    )
    sectioning_reason = (
        "" if sectioning_disposition == "sectioned" else "No strong semantic boundaries were admitted during intake."
    )
    quotation_readiness = (
        "restricted"
        if asr_disposition == "repaired"
        and speaker_attribution == "turn-labeled"
        and sectioning_disposition == "sectioned"
        else "not-ready"
    )
    quotation_reason = (
        "Usable for bounded analysis, but quotations require source-audio verification."
        if quotation_readiness == "restricted"
        else "Transcript processing is incomplete; quotations are not ready."
    )
    lines = [
        "---",
        f"ingest_date: {args.ingest_date}",
        f"pub_date: {args.pub_date}",
        f"kind: {args.kind}",
        f"source_form: {args.source_form}",
        "host_people:",
    ]

    if args.host_people:
        lines.extend([f"  - {item}" for item in args.host_people])
    else:
        lines.append("  -")

    lines.append("guest_people:")
    if args.guest_people:
        lines.extend([f"  - {item}" for item in args.guest_people])
    else:
        lines.append("  -")

    lines.extend(
        [
            f"show_title: {args.show_title}",
            f"channel_name: {args.channel_name}",
            f"host_slug: {host_slug}" if host_slug else "host_slug: \"\"",
            f"show: {args.show}",
            f"host: {args.host}",
            f"guest: {yaml_quote(args.guest)}",
            f"thread: {args.thread or args.voice_slugs[0]}",
            f"source_url: {yaml_quote(args.url)}",
            f"source_identity: {yaml_quote(getattr(args, 'source_identity', ''))}",
            f"source_url_status: {'provided' if args.url else 'unavailable'}",
            f"source_note: {yaml_quote(args.source_note)}",
            f"inference_basis: {yaml_quote(','.join(getattr(args, 'inference_basis', [])))}",
            f"title_source: {getattr(args, 'title_source', 'operator')}",
            f"title_aliases: {yaml_quote('|'.join(getattr(args, 'title_aliases', [])))}",
            f"title_confidence: {getattr(args, 'title_confidence', 'provisional')}",
            f"date_basis: {getattr(args, 'date_basis', 'operator-supplied')}",
            f"routing_basis: {getattr(args, 'routing_basis', 'inferred')}",
            f"source_form_basis: {getattr(args, 'source_form_basis', 'inferred')}",
            f"metadata_warnings: {yaml_quote('|'.join(getattr(args, 'metadata_warnings', [])))}",
            f"title_slug: {title_slug}",
            f"editorial_note: {yaml_quote(args.editorial_note)}",
            f"review_state: {args.review_state}",
            f"routing_state: {args.routing_state}",
            f"opening_trim_applied: {'true' if args.opening_trim_applied else 'false'}",
            f"opening_trim_rule: {yaml_quote(args.opening_trim_rule)}",
            f"opening_trim_chars_saved: {args.opening_trim_chars_saved}",
            f"opening_trim_words_saved: {args.opening_trim_words_saved}",
            f"closing_trim_applied: {'true' if args.closing_trim_applied else 'false'}",
            f"closing_trim_rule: {yaml_quote(args.closing_trim_rule)}",
            f"closing_trim_chars_saved: {args.closing_trim_chars_saved}",
            f"closing_trim_words_saved: {args.closing_trim_words_saved}",
            f"asr_repair_applied: {'true' if asr_repair_applied else 'false'}",
            f"asr_repair_pass: {yaml_quote(asr_repair_pass)}",
            f"transcript_curation: {args.transcript_curation}",
            f"section_count: {args.section_count}",
            f"section_pass: {yaml_quote(args.section_pass)}",
            f"asr_disposition: {asr_disposition}",
            f"speaker_attribution: {speaker_attribution}",
            f"speaker_attribution_reason: {yaml_quote(speaker_attribution_reason)}",
            f"sectioning_disposition: {sectioning_disposition}",
            f"sectioning_reason: {yaml_quote(sectioning_reason)}",
            f"quotation_readiness: {quotation_readiness}",
            f"quotation_readiness_reason: {yaml_quote(quotation_reason)}",
            "---",
            f"# {args.title}",
            "",
            "## Transcript",
            "",
            body.rstrip(),
            "",
        ]
    )
    return "\n".join(lines)


def load_manifest() -> dict:
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def archived_source_urls() -> dict[str, str]:
    """Read URL provenance from landed source front matter for deduplication."""
    urls: dict[str, str] = {}
    pattern = re.compile(r'^source_url:\s*["\']?(https?://[^"\'\s]+)', re.MULTILINE)
    for path in ARCHIVE_SOURCES_ROOT.rglob("source-*.md"):
        match = pattern.search(path.read_text(encoding="utf-8", errors="replace")[:12000])
        if match:
            urls[match.group(1)] = path.relative_to(REPO_ROOT).as_posix()
    return urls


def archived_source_identities() -> dict[str, str]:
    """Read source identity from current and legacy archive frontmatter."""
    identities: dict[str, str] = {}
    pattern = re.compile(r'^source_url:\s*["\']?(https?://[^"\'\s]+)', re.MULTILINE)
    identity_pattern = re.compile(r'^source_identity:\s*["\']?([^"\'\s]+)', re.MULTILINE)
    for path in ARCHIVE_SOURCES_ROOT.rglob("source-*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")[:12000]
        match = identity_pattern.search(text)
        identity = match.group(1) if match else ""
        if not identity:
            url_match = pattern.search(text)
            identity = canonical_source_identity(url_match.group(1)) if url_match else ""
        if identity:
            identities[identity] = path.relative_to(REPO_ROOT).as_posix()
    return identities


def write_manifest(manifest: dict) -> None:
    payload = manifest_bytes(manifest)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{MANIFEST_PATH.name}.", suffix=".stage", dir=MANIFEST_PATH.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, MANIFEST_PATH)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def manifest_bytes(manifest: dict) -> bytes:
    payload = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    json.loads(payload.decode("utf-8"))
    return payload


def build_manifest_row(
    args: SimpleNamespace,
    source_path: Path,
    upstream_path: str,
) -> dict:
    rel_local = source_path.relative_to(REPO_ROOT).as_posix()
    return {
        "date": args.pub_date,
        "title": args.title,
        "local_path": rel_local,
        "voice_index_path": f"../../../archive/sources/geopolitics/sources/{args.pub_date}/{source_path.name}",
        "upstream_path": upstream_path,
        "source_class": args.source_class,
        "modality": args.modality,
        "voice_slugs": args.voice_slugs,
        "host_slug": args.host_slug,
        "source_identity": getattr(args, "source_identity", ""),
        "source_url": args.url,
        "title_source": getattr(args, "title_source", "operator"),
        "date_basis": getattr(args, "date_basis", "operator-supplied"),
        "inference_basis": list(getattr(args, "inference_basis", [])),
        "import_status": "imported",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Land Narrative Geopolitics best-intake sources and append manifest rows."
    )
    parser.add_argument("--pub-date")
    parser.add_argument("--ingest-date")
    parser.add_argument("--date", help="Convenience date for both publication and ingest date; use 'today' for the current date.")
    parser.add_argument("--quick", action="store_true", help="Use inferred metadata with minimal required inputs.")
    parser.add_argument("quick_positionals", nargs="*", help=argparse.SUPPRESS)
    parser.add_argument("--title")
    parser.add_argument("--url")
    parser.add_argument("--body-file")
    parser.add_argument("--body-text")
    parser.add_argument("--voice-slug", dest="voice_slugs", action="append")
    parser.add_argument("--host-slug")
    parser.add_argument("--host", default="")
    parser.add_argument("--guest", default="")
    parser.add_argument("--host-people", action="append")
    parser.add_argument("--guest-people", action="append")
    parser.add_argument("--show-title", default="")
    parser.add_argument("--channel-name", default="")
    parser.add_argument("--show", default="")
    parser.add_argument("--thread")
    parser.add_argument("--kind", default="cleaned-transcript")
    parser.add_argument("--source-form", default="interview")
    parser.add_argument("--source-class", default="guest interview pressure test")
    parser.add_argument("--modality", default="cleaned-transcript")
    parser.add_argument("--review-state", default="unreviewed")
    parser.add_argument("--routing-state", default="provisional")
    parser.add_argument(
        "--source-note",
        default="Operator-pasted source body. Best-intake landing with preserved transcript body and provisional routing where needed.",
    )
    parser.add_argument(
        "--editorial-note",
        default="Preserve as raw cleaned transcript. Not human-verified verbatim.",
    )
    parser.add_argument(
        "--upstream-path",
        help="Optional upstream path. Defaults to an operator-paste URI based on ingest date and title.",
    )
    parser.add_argument(
        "--metadata-file",
        help="Read single-source metadata from an intake sidecar file.",
    )
    parser.add_argument(
        "--batch-dir",
        help="Read every metadata sidecar in a directory and land them as a batch.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned output paths and manifest rows without writing files.",
    )
    parser.add_argument("--preflight", action="store_true", help="Print a read-only intake preflight receipt.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable preflight or landing receipts.")
    parser.add_argument("--no-preflight", action="store_true", help="Skip internal preflight for controlled batch use.")
    parser.add_argument(
        "--trim-opening",
        choices=("auto", "none", *sorted(HOST_TRIM_RULES)),
        default="auto",
        help="Optionally trim known host preamble chatter before landing the source body.",
    )
    parser.add_argument(
        "--backfill-since",
        help="Retrofit approved trim rules onto already-landed archive sources with pub_date on or after this YYYY-MM-DD date.",
    )
    parser.add_argument(
        "--backfill-until",
        help="Optional inclusive end date for archive retrofit operations.",
    )
    parser.add_argument(
        "--sectioning",
        choices=("auto", "none"),
        default="auto",
        help="Apply conservative semantic transcript sectioning for approved hosts.",
    )
    parser.add_argument(
        "--asr-repair",
        choices=("auto", "none"),
        default="auto",
        help="Apply conservative ASR repair for approved transcript hosts before sectioning.",
    )
    parser.add_argument(
        "--force-sections",
        action="store_true",
        help="Allow retrofit operations to reprocess already sectioned transcripts.",
    )
    return parser.parse_args()


def ensure_required_fields(args: SimpleNamespace) -> None:
    missing = []
    if not getattr(args, "pub_date", None):
        missing.append("pub_date")
    if not getattr(args, "ingest_date", None):
        missing.append("ingest_date")
    if not getattr(args, "title", None):
        missing.append("title")
    body_file = getattr(args, "body_file", None)
    body_text = getattr(args, "body_text", None)
    if not body_file and not body_text:
        missing.append("body")
    if not getattr(args, "voice_slugs", None):
        missing.append("voice_slug")
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    args.pub_date = validate_iso_date(args.pub_date, "pub_date")
    args.ingest_date = validate_iso_date(args.ingest_date, "ingest_date")
    args.url = (getattr(args, "url", None) or "").strip()


def resolve_quick_inputs(args: SimpleNamespace) -> None:
    if not getattr(args, "quick", False):
        if getattr(args, "quick_positionals", None):
            raise ValueError("Positional host/URL inputs require --quick.")
        return
    positionals = list(getattr(args, "quick_positionals", []) or [])
    if positionals:
        if len(positionals) > 2:
            raise ValueError("Quick intake accepts at most HOST and URL positionals.")
        for value in positionals:
            if value.startswith("http://") or value.startswith("https://"):
                if args.url:
                    raise ValueError("URL supplied more than once.")
                args.url = value
            elif not args.host_slug:
                args.host_slug = value
            else:
                raise ValueError(f"Unrecognized quick positional input: {value}")
    supplied_date = getattr(args, "date", None)
    if supplied_date:
        if supplied_date == "today":
            supplied_date = date.today().isoformat()
            args.date_assignment = "intake-assigned-today"
        else:
            supplied_date = validate_iso_date(supplied_date, "date")
            args.date_assignment = "explicit-date-alias"
        args.pub_date = args.pub_date or supplied_date
        args.ingest_date = args.ingest_date or supplied_date
    if not args.pub_date or not args.ingest_date:
        raise ValueError("Quick intake requires --date, --pub-date, or --ingest-date.")


def validate_iso_date(value: object, label: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError(f"{label} must be a valid YYYY-MM-DD date")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != value:
        raise ValueError(f"{label} must be a valid YYYY-MM-DD date")
    return value


def normalize_args(args: SimpleNamespace) -> SimpleNamespace:
    resolve_quick_inputs(args)
    add_metadata_defaults(args)
    infer_missing_metadata(args)
    args.host_people = [item for item in (args.host_people or []) if item]
    args.guest_people = [item for item in (args.guest_people or []) if item]
    args.voice_slugs = [item for item in (args.voice_slugs or []) if item]
    ensure_required_fields(args)
    return args


def parse_metadata_file(path: Path) -> dict[str, object]:
    data: dict[str, object] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if key in REPEATABLE_FIELDS:
            items = data.setdefault(key, [])
            if value:
                assert isinstance(items, list)
                items.append(value)
        else:
            data[key] = value
    return data


def args_from_metadata(metadata: dict[str, object], metadata_path: Path, cli_args: argparse.Namespace) -> SimpleNamespace:
    defaults = {
        "host_slug": None,
        "host": "",
        "guest": "",
        "host_people": [],
        "guest_people": [],
        "show_title": "",
        "channel_name": "",
        "show": "",
        "thread": None,
        "kind": "cleaned-transcript",
        "source_form": "interview",
        "source_class": "guest interview pressure test",
        "modality": "cleaned-transcript",
        "review_state": "unreviewed",
        "routing_state": "provisional",
        "source_note": "Operator-pasted source body. Best-intake landing with preserved transcript body and provisional routing where needed.",
        "editorial_note": "Preserve as raw cleaned transcript. Not human-verified verbatim.",
        "upstream_path": None,
        "trim_opening": "auto",
        "asr_repair": "auto",
        "sectioning": "auto",
        "quick": False,
        "quick_positionals": [],
        "date": None,
    }
    mapped = defaults.copy()
    mapped.update(
        {
            "pub_date": metadata.get("pub_date", ""),
            "ingest_date": metadata.get("ingest_date", ""),
            "title": metadata.get("title", ""),
            "url": metadata.get("url", ""),
            "body_file": metadata.get("body_file", ""),
            "body_text": metadata.get("body_text", ""),
            "voice_slugs": metadata.get("voice_slug", []),
            "host_slug": metadata.get("host_slug") or None,
            "host": metadata.get("host", ""),
            "guest": metadata.get("guest", ""),
            "host_people": metadata.get("host_people", []),
            "guest_people": metadata.get("guest_people", []),
            "show_title": metadata.get("show_title", ""),
            "channel_name": metadata.get("channel_name", ""),
            "show": metadata.get("show", ""),
            "thread": metadata.get("thread") or None,
            "kind": metadata.get("kind", defaults["kind"]),
            "source_form": metadata.get("source_form", defaults["source_form"]),
            "source_class": metadata.get("source_class", defaults["source_class"]),
            "modality": metadata.get("modality", defaults["modality"]),
            "review_state": metadata.get("review_state", defaults["review_state"]),
            "routing_state": metadata.get("routing_state", defaults["routing_state"]),
            "source_note": metadata.get("source_note", defaults["source_note"]),
            "editorial_note": metadata.get("editorial_note", defaults["editorial_note"]),
            "upstream_path": metadata.get("upstream_path") or None,
            "trim_opening": metadata.get("trim_opening", defaults["trim_opening"]),
            "asr_repair": metadata.get("asr_repair", defaults["asr_repair"]),
            "quick": cli_args.quick,
            "quick_positionals": [],
            "date": cli_args.date,
        }
    )
    if mapped["body_file"]:
        body_file = Path(str(mapped["body_file"]))
        if not body_file.is_absolute():
            mapped["body_file"] = str((metadata_path.parent / body_file).resolve())
    mapped["dry_run"] = cli_args.dry_run
    mapped["opening_trim_applied"] = False
    mapped["opening_trim_rule"] = ""
    mapped["opening_trim_chars_saved"] = 0
    mapped["opening_trim_words_saved"] = 0
    mapped["closing_trim_applied"] = False
    mapped["closing_trim_rule"] = ""
    mapped["closing_trim_chars_saved"] = 0
    mapped["closing_trim_words_saved"] = 0
    mapped["transcript_curation"] = "preserved_unsectioned"
    mapped["section_count"] = 0
    mapped["section_pass"] = SECTIONING_PASS_LABEL
    mapped["asr_repair_applied"] = False
    mapped["asr_repair_pass"] = ""
    mapped["inference_basis"] = []
    mapped["date_assignment"] = ""
    return normalize_args(SimpleNamespace(**mapped))


def args_from_cli(cli_args: argparse.Namespace, *, normalize: bool = True) -> SimpleNamespace:
    mapped = {
        "pub_date": cli_args.pub_date,
        "ingest_date": cli_args.ingest_date,
        "title": cli_args.title,
        "url": cli_args.url,
        "body_file": cli_args.body_file,
        "body_text": cli_args.body_text,
        "voice_slugs": cli_args.voice_slugs,
        "host_slug": cli_args.host_slug,
        "host": cli_args.host,
        "guest": cli_args.guest,
        "host_people": cli_args.host_people,
        "guest_people": cli_args.guest_people,
        "show_title": cli_args.show_title,
        "channel_name": cli_args.channel_name,
        "show": cli_args.show,
        "thread": cli_args.thread,
        "kind": cli_args.kind,
        "source_form": cli_args.source_form,
        "source_class": cli_args.source_class,
        "modality": cli_args.modality,
        "review_state": cli_args.review_state,
        "routing_state": cli_args.routing_state,
        "source_note": cli_args.source_note,
        "editorial_note": cli_args.editorial_note,
        "upstream_path": cli_args.upstream_path,
        "dry_run": cli_args.dry_run,
        "trim_opening": cli_args.trim_opening,
        "asr_repair": cli_args.asr_repair,
        "sectioning": cli_args.sectioning,
        "quick": cli_args.quick,
        "quick_positionals": cli_args.quick_positionals,
        "date": cli_args.date,
        "date_assignment": "",
        "inference_basis": [],
        "opening_trim_applied": False,
        "opening_trim_rule": "",
        "opening_trim_chars_saved": 0,
        "opening_trim_words_saved": 0,
        "closing_trim_applied": False,
        "closing_trim_rule": "",
        "closing_trim_chars_saved": 0,
        "closing_trim_words_saved": 0,
        "transcript_curation": "preserved_unsectioned",
        "section_count": 0,
        "section_pass": SECTIONING_PASS_LABEL,
        "asr_repair_applied": False,
        "asr_repair_pass": "",
        "title_aliases": [],
        "metadata_warnings": [],
        "title_source": "operator" if cli_args.title else "transcript",
        "title_confidence": "provisional",
        "date_basis": "operator-supplied",
        "routing_basis": "inferred",
        "source_form_basis": "inferred",
    }
    args = SimpleNamespace(**mapped)
    return normalize_args(args) if normalize else args


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def normalize_body_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized if normalized.endswith("\n") else normalized + "\n"


def load_body_text(args: SimpleNamespace) -> str:
    cached = getattr(args, "_body_text_cache", None)
    if isinstance(cached, str):
        return cached
    body_text = getattr(args, "body_text", None)
    if isinstance(body_text, str) and body_text.strip():
        normalized = normalize_body_text(body_text)
        args._body_text_cache = normalized
        return normalized
    body_file = getattr(args, "body_file", None)
    if body_file:
        normalized = normalize_body_text(Path(body_file).read_text(encoding="utf-8"))
        args._body_text_cache = normalized
        return normalized
    return ""


def strip_exact_outer_wrappers(body: str) -> str:
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and re.fullmatch(r".+\s+-\s+YouTube\s*", lines[0].strip(), flags=re.IGNORECASE):
        lines.pop(0)
        if lines and lines[0].strip().lower() == "transcripts:":
            lines.pop(0)
    return normalize_body_text("\n".join(lines).lstrip("\n"))


def parse_title_from_body(body: str) -> str:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        return ""
    first = lines[0]
    if not re.search(r"-\s*YouTube(?:\s+Transcripts?)?\s*$", first, re.IGNORECASE) and "youtube transcripts:" not in first.lower() and not (len(lines) > 1 and lines[1].lower().startswith("transcripts:")):
        return ""
    first = re.sub(r"\s*Transcripts?:.*$", "", first, flags=re.IGNORECASE)
    first = re.sub(r"\s*-\s*YouTube(?:\s+Transcripts?)?.*$", "", first, flags=re.IGNORECASE)
    first = re.sub(r"\s{2,}", " ", first).strip(" -:")
    if len(first) >= 8:
        return first
    return ""


def youtube_video_id(url: str) -> str:
    match = re.search(r"(?:[?&]v=|youtu\.be/|youtube\.com/shorts/)([A-Za-z0-9_-]{6,})", url or "")
    return match.group(1) if match else ""


def canonical_source_identity(url: str) -> str:
    video_id = youtube_video_id(url)
    if video_id:
        return f"youtube:{video_id}"
    return (url or "").strip().rstrip("/")


def transcript_date_basis(body: str, pub_date: str) -> str:
    if re.search(r"\b(?:today is|today's)\s+(?:\w+,\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december)\b", body, re.IGNORECASE):
        return "transcript-self-date"
    return "operator-supplied" if pub_date else "unknown"


def add_metadata_defaults(args: SimpleNamespace) -> None:
    args.source_identity = canonical_source_identity(getattr(args, "url", ""))
    args.title_aliases = list(getattr(args, "title_aliases", []))
    args.metadata_warnings = list(getattr(args, "metadata_warnings", []))
    args.title_source = getattr(args, "title_source", "operator" if getattr(args, "title", "") else "transcript")
    args.title_confidence = getattr(args, "title_confidence", "provisional")
    args.date_basis = getattr(args, "date_basis", "operator-supplied")
    args.routing_basis = getattr(args, "routing_basis", "inferred")
    args.source_form_basis = getattr(args, "source_form_basis", "inferred")


def apply_transcript_title(args: SimpleNamespace, body: str) -> None:
    supplied_title = (getattr(args, "title", "") or "").strip()
    transcript_title = parse_title_from_body(body)
    if transcript_title:
        if supplied_title and supplied_title != transcript_title:
            args.title_aliases = [supplied_title]
            args.metadata_warnings.append("operator-title-differs-from-transcript-title")
        args.title = transcript_title
        args.title_source = "transcript"
        args.title_confidence = "high"
    elif supplied_title:
        args.title_source = "operator"
        args.title_confidence = "provisional"


def source_identity_matches(item: dict, identity: str, url: str) -> bool:
    if not identity and not url:
        return False
    candidate = str(item.get("source_identity") or "").strip()
    if candidate and candidate == identity:
        return True
    candidate_url = str(item.get("source_url") or item.get("url") or "").strip().rstrip("/")
    return bool(candidate_url and candidate_url == (url or "").strip().rstrip("/"))


def title_from_url(url: str) -> str:
    match = re.search(r"[?&]v=([A-Za-z0-9_-]+)", url or "")
    if match:
        return f"youtube-{match.group(1)}"
    return "untitled-source"


def apply_host_profile(args: SimpleNamespace, profile: HostProfile) -> None:
    if getattr(args, "host_slug", None) == profile.slug:
        args.inference_basis.append("explicit-host")
    else:
        args.inference_basis.append("host-profile")
    args.host_slug = args.host_slug or profile.slug
    args.host = args.host or profile.host_name
    args.host_people = [item for item in (args.host_people or profile.host_people) if item]
    args.channel_name = args.channel_name or profile.channel_name
    args.show_title = args.show_title or profile.show_title
    args.show = args.show or profile.show


def infer_host_profile(args: SimpleNamespace, body: str) -> HostProfile | None:
    if getattr(args, "host_slug", None):
        return HOST_PROFILES.get(args.host_slug)
    combined = " ".join(
        item for item in (getattr(args, "title", ""), getattr(args, "url", ""), body[:4000]) if item
    ).lower()
    for pattern, slug in HOST_CUE_PATTERNS:
        if re.search(pattern, combined):
            args.inference_basis.append("title-cue" if getattr(args, "title", "") and re.search(pattern, getattr(args, "title", "").lower()) else "body-cue")
            return HOST_PROFILES[slug]
    for profile in HOST_PROFILES.values():
        if any(alias in combined for alias in profile.aliases):
            args.inference_basis.append("title-cue" if getattr(args, "title", "") and any(alias in getattr(args, "title", "").lower() for alias in profile.aliases) else "body-cue")
            return profile
    return None


def infer_voice_candidates(text: str) -> list[tuple[str, str]]:
    lowered = text.lower()
    matches: list[tuple[str, str]] = []
    seen: set[str] = set()
    for needle, slug, display_name in VOICE_HINTS:
        if needle in lowered and slug not in seen:
            matches.append((slug, display_name))
            seen.add(slug)
    return matches


def infer_source_form(args: SimpleNamespace, body: str, profile: HostProfile | None, voice_candidates: list[tuple[str, str]]) -> str:
    explicit = getattr(args, "source_form", "") or ""
    if explicit not in ("", "interview"):
        return explicit
    title = getattr(args, "title", "")
    combined = f"{title}\n{body[:2500]}".lower()
    if "welcome back to neutrality studies" in combined:
        return "interview"
    if getattr(args, "guest", "") or getattr(args, "guest_people", None):
        return "interview"
    if profile and getattr(args, "voice_slugs", None):
        if any(slug != profile.default_voice_slug for slug in args.voice_slugs):
            return "interview"
    if voice_candidates and profile and any(slug != profile.default_voice_slug for slug, _ in voice_candidates):
        return "interview"
    if profile and profile.slug in {"alexander-mercouris", "daniel-davis"}:
        unresolved_guest = re.search(
            r"(?:\bwith\b|\bw/)\s+"
            r"(?!(?:the|a|an|our|this|why|how)\b)"
            r"(?:[A-Z][A-Za-z.'’-]*\s+){1,3}[A-Z][A-Za-z.'’-]*\b",
            title,
        )
        if unresolved_guest:
            raise ValueError(
                "Need one clarification: the title suggests an unrecognized guest. "
                "Re-run with --guest and --voice-slug, or use --source-form solo/monologue "
                "when no guest is present."
            )
    if profile and profile.slug == "alexander-mercouris":
        return "solo"
    if profile and profile.slug == "daniel-davis":
        return "monologue"
    return profile.default_source_form if profile else "interview"


def infer_defaults_for_source_form(args: SimpleNamespace) -> None:
    if getattr(args, "kind", "") in ("", None):
        args.kind = "cleaned-transcript"
    if getattr(args, "modality", "") in ("", None):
        args.modality = "cleaned-transcript"
    if getattr(args, "source_form", "") in ("solo", "monologue"):
        if getattr(args, "source_class", "") in ("", None, "guest interview pressure test"):
            args.source_class = "host monologue"
    elif getattr(args, "source_class", "") in ("", None):
        args.source_class = "guest interview pressure test"


def infer_missing_metadata(args: SimpleNamespace) -> SimpleNamespace:
    args.inference_basis = list(getattr(args, "inference_basis", []))
    args.date_assignment = getattr(args, "date_assignment", "")
    body = load_body_text(args)
    if not body:
        return args
    apply_transcript_title(args, body)
    args.date_basis = transcript_date_basis(body, getattr(args, "pub_date", ""))
    if not getattr(args, "ingest_date", None) and getattr(args, "pub_date", None):
        args.ingest_date = args.pub_date
    if not getattr(args, "pub_date", None) and getattr(args, "ingest_date", None):
        args.pub_date = args.ingest_date
    if not getattr(args, "title", None):
        args.title = parse_title_from_body(body) or title_from_url(getattr(args, "url", ""))
        args.inference_basis.append("title-cue")

    if getattr(args, "quick", False):
        body = strip_exact_outer_wrappers(body)
        args._body_text_cache = body
        args.inference_basis.append("wrapper-normalized")

    profile = infer_host_profile(args, body)
    if profile:
        apply_host_profile(args, profile)

    combined = f"{getattr(args, 'title', '')}\n{body[:4000]}"
    voice_candidates = infer_voice_candidates(combined)
    host_voice = profile.default_voice_slug if profile else None
    guest_candidates = [(slug, name) for slug, name in voice_candidates if slug != host_voice]

    if not getattr(args, "voice_slugs", None):
        if len(guest_candidates) == 1:
            args.voice_slugs = [guest_candidates[0][0]]
        elif len(guest_candidates) > 1:
            labels = ", ".join(slug for slug, _ in guest_candidates[:3])
            raise ValueError(
                f"Need one clarification: primary guest/voice is ambiguous ({labels}). Re-run with --voice-slug."
            )
        elif profile and profile.default_voice_slug:
            args.voice_slugs = [profile.default_voice_slug]

    if not getattr(args, "guest", "") and len(guest_candidates) == 1:
        args.guest = guest_candidates[0][1]
    if not getattr(args, "guest_people", None) and getattr(args, "guest", ""):
        args.guest_people = [args.guest]

    if not profile and not getattr(args, "host_slug", None):
        raise ValueError("Need one clarification: I could not infer the host/channel. Re-run with --host-slug.")

    args.source_form = infer_source_form(args, body, profile, voice_candidates)
    args.source_form_basis = "explicit" if getattr(args, "source_form", "") not in ("", "interview") else "inferred"
    args.routing_basis = "explicit-host" if "explicit-host" in args.inference_basis else "host-profile-or-body-cue"
    infer_defaults_for_source_form(args)
    if not getattr(args, "thread", None) and getattr(args, "voice_slugs", None):
        args.thread = args.voice_slugs[0]
    if getattr(args, "date_assignment", ""):
        args.inference_basis.append(args.date_assignment)
    return args


def get_trim_rule(args: SimpleNamespace) -> HostTrimRule | None:
    trim_mode = getattr(args, "trim_opening", "auto")
    if trim_mode == "none":
        return None
    if trim_mode == "auto":
        host_slug = getattr(args, "host_slug", None)
        if not host_slug:
            return None
        return HOST_TRIM_RULES.get(host_slug)
    return HOST_TRIM_RULES.get(trim_mode)


def trim_opening_by_rule(body: str, rule: HostTrimRule) -> tuple[str, bool, str, int, int]:
    normalized = body.lstrip()
    for pattern in rule.opening_regexes:
        match = re.match(pattern, normalized)
        if match:
            trimmed = normalized[match.end():].lstrip()
            if trimmed:
                removed = normalized[: match.end()]
                return trimmed, True, rule.label, len(removed), count_words(removed)
    for marker in rule.opening_markers:
        idx = normalized.find(marker)
        if idx > 0:
            trimmed = normalized[idx:].lstrip()
            if trimmed:
                removed = normalized[:idx]
                return trimmed, True, rule.label, len(removed), count_words(removed)
    for snippet in rule.opening_snippets:
        idx = normalized.find(snippet)
        if 0 <= idx <= 400:
            removed = ""
            replacements = (
                (f" {snippet} ", " "),
                (f"{snippet} ", ""),
                (snippet, ""),
            )
            trimmed = normalized
            for candidate, replacement in replacements:
                candidate_idx = trimmed.find(candidate)
                if 0 <= candidate_idx <= 400:
                    removed = candidate
                    trimmed = trimmed.replace(candidate, replacement, 1)
                    break
            trimmed = re.sub(r"(?<=\S) {2,}", " ", trimmed, count=1)
            if trimmed and removed:
                return trimmed, True, rule.label, len(removed), count_words(removed)
    return body, False, "", 0, 0


def trim_closing_by_rule(body: str, rule: HostTrimRule) -> tuple[str, bool, str, int, int]:
    cut_index = -1
    for marker in rule.closing_markers:
        idx = body.find(marker)
        if idx >= 0 and (cut_index == -1 or idx < cut_index):
            cut_index = idx
    if cut_index >= 0:
        trimmed = body[:cut_index].rstrip()
        if trimmed:
            removed = body[cut_index:]
            return trimmed + "\n", True, rule.label, len(removed), count_words(removed)
    return body, False, "", 0, 0


def maybe_trim_opening(args: SimpleNamespace, body: str) -> tuple[str, bool, str, int, int]:
    rule = get_trim_rule(args)
    if not rule or (not rule.opening_markers and not rule.opening_snippets and not rule.opening_regexes):
        return body, False, "", 0, 0
    return trim_opening_by_rule(body, rule)


def maybe_trim_closing(args: SimpleNamespace, body: str) -> tuple[str, bool, str, int, int]:
    rule = get_trim_rule(args)
    if not rule or not rule.closing_markers:
        return body, False, "", 0, 0
    return trim_closing_by_rule(body, rule)


def apply_trim_metadata(args: SimpleNamespace, body: str) -> str:
    prior_opening = (
        getattr(args, "opening_trim_applied", False),
        getattr(args, "opening_trim_rule", ""),
        getattr(args, "opening_trim_chars_saved", 0),
        getattr(args, "opening_trim_words_saved", 0),
    )
    prior_closing = (
        getattr(args, "closing_trim_applied", False),
        getattr(args, "closing_trim_rule", ""),
        getattr(args, "closing_trim_chars_saved", 0),
        getattr(args, "closing_trim_words_saved", 0),
    )

    body, opening_trim_applied, opening_trim_rule, opening_trim_chars_saved, opening_trim_words_saved = maybe_trim_opening(args, body)
    if opening_trim_applied:
        args.opening_trim_applied = opening_trim_applied
        args.opening_trim_rule = opening_trim_rule
        args.opening_trim_chars_saved = opening_trim_chars_saved
        args.opening_trim_words_saved = opening_trim_words_saved
    else:
        (
            args.opening_trim_applied,
            args.opening_trim_rule,
            args.opening_trim_chars_saved,
            args.opening_trim_words_saved,
        ) = prior_opening

    body, closing_trim_applied, closing_trim_rule, closing_trim_chars_saved, closing_trim_words_saved = maybe_trim_closing(args, body)
    if closing_trim_applied:
        args.closing_trim_applied = closing_trim_applied
        args.closing_trim_rule = closing_trim_rule
        args.closing_trim_chars_saved = closing_trim_chars_saved
        args.closing_trim_words_saved = closing_trim_words_saved
    else:
        (
            args.closing_trim_applied,
            args.closing_trim_rule,
            args.closing_trim_chars_saved,
            args.closing_trim_words_saved,
        ) = prior_closing
    return body


def host_supports_asr_repair(host_slug: str | None) -> bool:
    return bool(host_slug and host_slug in ASR_REPAIR_APPROVED_HOSTS)


def repair_asr_text(
    args: SimpleNamespace,
    body: str,
    *,
    normalize_layout: bool = True,
) -> str:
    prior_applied = bool(getattr(args, "asr_repair_applied", False))
    prior_pass = getattr(args, "asr_repair_pass", "")

    def preserve_prior_metadata() -> None:
        args.asr_repair_applied = prior_applied
        args.asr_repair_pass = prior_pass

    if getattr(args, "asr_repair", "auto") == "none":
        preserve_prior_metadata()
        return body
    if not host_supports_asr_repair(getattr(args, "host_slug", None)):
        preserve_prior_metadata()
        return body

    repaired = body
    for pattern, replacement in GLOBAL_ASR_REPAIRS:
        repaired = re.sub(pattern, replacement, repaired)
    for pattern, replacement in HOST_ASR_REPAIRS.get(getattr(args, "host_slug", None), ()):
        repaired = re.sub(pattern, replacement, repaired)

    if normalize_layout:
        repaired = re.sub(r"\n{3,}", "\n\n", repaired).strip() + "\n"
    if repaired != body:
        args.asr_repair_applied = True
        args.asr_repair_pass = ASR_REPAIR_PASS_LABEL
    else:
        preserve_prior_metadata()
    return repaired


def host_supports_sectioning(host_slug: str | None) -> bool:
    return bool(host_slug and host_slug in SECTIONING_APPROVED_HOSTS)


def cleanup_section_label(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip(" -,:;.!?\n\t")
    cleaned = re.sub(r"^[^A-Za-z0-9]+", "", cleaned)
    if not cleaned:
        return ""
    words = [
        word
        for word in cleaned.split()
        if word.lower() not in TOPIC_STOPWORDS and word.lower() not in TOPIC_FILLER_WORDS
    ]
    if not words:
        return ""
    if len(words) > 8:
        words = words[:8]
    cleaned = " ".join(words)
    return cleaned.title()


def format_topic_token(token: str) -> str:
    upper = token.upper()
    if upper in UPPERCASE_TOPIC_TOKENS:
        return upper
    return token.title()


def ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def extract_topic_candidates(block: str, title: str) -> list[str]:
    lowered = block.lower()
    phrase_candidates: list[str] = []
    for phrase in DOMAIN_TOPIC_PHRASES:
        if phrase in lowered:
            phrase_candidates.append(phrase)

    token_matches = re.findall(r"[A-Za-z][A-Za-z'-]+", block)
    counts: dict[str, int] = {}
    for token in token_matches:
        lowered_token = token.lower()
        if lowered_token in TOPIC_STOPWORDS or lowered_token in TOPIC_FILLER_WORDS:
            continue
        if len(lowered_token) < 3:
            continue
        counts[lowered_token] = counts.get(lowered_token, 0) + 1

    phrase_candidates.sort(
        key=lambda phrase: (
            lowered.count(phrase),
            len(phrase.split()),
            len(phrase),
        ),
        reverse=True,
    )

    candidates: list[str] = []
    for phrase in phrase_candidates[:4]:
        candidates.append(phrase)

    for token in token_matches:
        lowered_token = token.lower()
        if lowered_token not in counts:
            continue
        if counts[lowered_token] >= 2:
            candidates.append(lowered_token)

    return ordered_unique(candidates)


def derive_topic_label(block: str, title: str) -> str:
    candidates = extract_topic_candidates(block, title)
    if not candidates:
        return ""

    label_parts: list[str] = []
    for candidate in candidates:
        if " " in candidate:
            label_parts.append(cleanup_section_label(candidate))
        else:
            label_parts.append(format_topic_token(candidate))
        if len(label_parts) >= 3:
            break

    label = " ".join(part for part in label_parts if part)
    return cleanup_section_label(label)


def paragraph_is_boundary(paragraph: str) -> bool:
    lowered = paragraph.lower().strip()
    if not lowered:
        return False
    cues = (
        "let me start",
        "let's start",
        "i want to ask",
        "what do you make of",
        "let's go to",
        "another point",
        "the other issue",
        "first of all",
        "secondly",
        "thirdly",
        "turning to",
        "let me turn to",
        "let's turn to",
        "now let me",
        "now on",
        "another thing",
        "another issue",
        "on the other hand",
        "meanwhile",
        "now,",
        "now ",
    )
    return any(cue in lowered for cue in cues)


def split_transcript_paragraphs(body: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", body.strip())
    return [block.strip() for block in blocks if block.strip()]


def normalize_inline_turn_markers(body: str) -> str:
    """Expose source-supplied YouTube turn markers without assigning identities."""
    if ">>" not in body:
        return body
    normalized = re.sub(r"[ \t]*>>[ \t]*", "\n\n>> ", body)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip() + "\n"
    return normalized


def format_sectioned_body(sections: list[tuple[str, str]]) -> str:
    chunks: list[str] = []
    for heading, block in sections:
        chunks.append(f"### {heading}\n\n{block.strip()}")
    return "\n\n".join(chunks).rstrip() + "\n"


def strip_transcript_section_headings(body: str) -> str:
    lines = body.splitlines()
    kept: list[str] = []
    previous_blank = False
    for line in lines:
        if re.match(r"^### ", line):
            continue
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        kept.append(line)
        previous_blank = is_blank
    return "\n".join(kept).strip() + "\n"


def split_source_document(text: str) -> tuple[list[str], str, str] | None:
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter_lines = parts[1].splitlines()
    content = parts[2]
    for transcript_heading in ("## Transcript", "## Cleaned Transcript"):
        if transcript_heading in content:
            body_prefix, transcript_body = content.split(transcript_heading, 1)
            return frontmatter_lines, body_prefix + transcript_heading + "\n\n", transcript_body.lstrip()

    heading_match = re.search(r"(?m)^# .+\n", content)
    if not heading_match:
        return None
    after_heading = content[heading_match.end():]
    metadata_block_match = re.match(r"(?:\n|[^\n]*\n)*(?:\n){2}", after_heading)
    if metadata_block_match:
        prefix = content[: heading_match.end() + metadata_block_match.end()]
        body = content[heading_match.end() + metadata_block_match.end():]
        return frontmatter_lines, prefix, body.lstrip()
    return frontmatter_lines, content[: heading_match.end() + len(after_heading)], ""


def parse_frontmatter_lines(lines: list[str]) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def unquote_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def truthy_scalar(value: str | None) -> bool:
    return unquote_scalar(value or "").lower() == "true"


def build_trim_field_lines(args: SimpleNamespace) -> list[str]:
    return [
        f"opening_trim_applied: {'true' if args.opening_trim_applied else 'false'}",
        f"opening_trim_rule: {yaml_quote(args.opening_trim_rule)}",
        f"opening_trim_chars_saved: {args.opening_trim_chars_saved}",
        f"opening_trim_words_saved: {args.opening_trim_words_saved}",
        f"closing_trim_applied: {'true' if args.closing_trim_applied else 'false'}",
        f"closing_trim_rule: {yaml_quote(args.closing_trim_rule)}",
        f"closing_trim_chars_saved: {args.closing_trim_chars_saved}",
        f"closing_trim_words_saved: {args.closing_trim_words_saved}",
    ]


def build_section_field_lines(args: SimpleNamespace) -> list[str]:
    return [
        f"transcript_curation: {args.transcript_curation}",
        f"section_count: {args.section_count}",
        f"section_pass: {yaml_quote(args.section_pass)}",
    ]


def build_asr_field_lines(args: SimpleNamespace) -> list[str]:
    return [
        f"asr_repair_applied: {'true' if args.asr_repair_applied else 'false'}",
        f"asr_repair_pass: {yaml_quote(args.asr_repair_pass)}",
    ]


def build_processing_field_lines(args: SimpleNamespace, body: str) -> list[str]:
    asr_disposition = "repaired" if args.asr_repair_applied else "needs-repair"
    speaker_attribution = "turn-labeled" if len(re.findall(r"(?m)^>> ", body)) >= 2 else "unknown"
    speaker_reason = (
        "Source transcript preserves explicit turn boundaries; identities are not assigned where the source does not establish them."
        if speaker_attribution == "turn-labeled"
        else "Source-level host and guest metadata does not establish transcript turn attribution."
    )
    sectioning_disposition = (
        "sectioned" if args.transcript_curation == "curated_sectioned" else "preserved-unsectioned"
    )
    sectioning_reason = (
        "" if sectioning_disposition == "sectioned" else "No strong semantic boundaries were admitted during intake."
    )
    quotation_readiness = (
        "restricted"
        if asr_disposition == "repaired"
        and speaker_attribution == "turn-labeled"
        and sectioning_disposition == "sectioned"
        else "not-ready"
    )
    quotation_reason = (
        "Usable for bounded analysis, but quotations require source-audio verification."
        if quotation_readiness == "restricted"
        else "Transcript processing is incomplete; quotations are not ready."
    )
    return [
        f"asr_disposition: {asr_disposition}",
        f"speaker_attribution: {speaker_attribution}",
        f"speaker_attribution_reason: {yaml_quote(speaker_reason)}",
        f"sectioning_disposition: {sectioning_disposition}",
        f"sectioning_reason: {yaml_quote(sectioning_reason)}",
        f"quotation_readiness: {quotation_readiness}",
        f"quotation_readiness_reason: {yaml_quote(quotation_reason)}",
    ]


def normalize_frontmatter_trim_fields(frontmatter_lines: list[str], args: SimpleNamespace, body: str) -> list[str]:
    new_lines: list[str] = []
    inserted = False
    for line in frontmatter_lines:
        stripped = line.strip()
        key = stripped.split(":", 1)[0] if ":" in stripped else ""
        if key in TRIM_FIELD_ORDER or key in ASR_FIELD_ORDER or key in SECTIONING_FIELD_ORDER or key in PROCESSING_FIELD_ORDER:
            continue
        if key == "editorial_note":
            new_lines.append(f"editorial_note: {yaml_quote(args.editorial_note)}")
            continue
        new_lines.append(line)
        if key == "routing_state":
            new_lines.extend(build_trim_field_lines(args))
            new_lines.extend(build_asr_field_lines(args))
            new_lines.extend(build_section_field_lines(args))
            new_lines.extend(build_processing_field_lines(args, body))
            inserted = True

    if not inserted:
        new_lines.extend(build_trim_field_lines(args))
        new_lines.extend(build_asr_field_lines(args))
        new_lines.extend(build_section_field_lines(args))
        new_lines.extend(build_processing_field_lines(args, body))
    return new_lines


def section_transcript(args: SimpleNamespace, body: str) -> tuple[str, str, int, str]:
    args.section_pass = SECTIONING_PASS_LABEL
    if getattr(args, "sectioning", "auto") == "none":
        return body, "preserved_unsectioned", 0, "disabled"
    if not host_supports_sectioning(getattr(args, "host_slug", None)):
        return body, "preserved_unsectioned", 0, "host-unapproved"
    if re.search(r"(?m)^### ", body):
        return body, "curated_sectioned", len(re.findall(r"(?m)^### ", body)), "already-sectioned"

    paragraphs = split_transcript_paragraphs(body)
    if len(paragraphs) < 3:
        return body, "preserved_unsectioned", 0, "too-short"

    boundary_indexes = [idx for idx, paragraph in enumerate(paragraphs[1:], start=1) if paragraph_is_boundary(paragraph)]
    if len(boundary_indexes) < 1:
        return body, "preserved_unsectioned", 0, "weak-cues"

    split_points = [0]
    for idx in boundary_indexes:
        if idx - split_points[-1] >= 1:
            split_points.append(idx)
    split_points.append(len(paragraphs))

    raw_sections: list[str] = []
    for start, end in zip(split_points, split_points[1:]):
        block = "\n\n".join(paragraphs[start:end]).strip()
        if block:
            raw_sections.append(block)

    if len(raw_sections) < 2:
        return body, "preserved_unsectioned", 0, "weak-cues"

    sections: list[tuple[str, str]] = []
    for index, block in enumerate(raw_sections, start=1):
        if index == 1:
            label = derive_topic_label(block, args.title) or derive_topic_label(" ".join(paragraphs[1:3]), args.title)
            if not label:
                return body, "preserved_unsectioned", 0, "unclean-open-label"
            heading = f"Show Open - {label}"
        elif index == len(raw_sections) and re.search(r"\b(thanks|thank you|goodbye|see you)\b", block, re.IGNORECASE):
            label = derive_topic_label(block, args.title)
            if not label:
                return body, "preserved_unsectioned", 0, "unclean-closing-label"
            heading = f"Closing - {label}"
        else:
            label = derive_topic_label(block, args.title)
            if not label:
                return body, "preserved_unsectioned", 0, "unclean-segment-label"
            heading = f"Segment {index} - {label}"
        sections.append((heading, block))

    if len(sections) < 2:
        return body, "preserved_unsectioned", 0, "weak-cues"
    return format_sectioned_body(sections), "curated_sectioned", len(sections), ""


def update_editorial_note(editorial_note: str, curation: str, section_count: int) -> str:
    cleaned = re.sub(r"\s*-\s*source-section pass [^.]+\.", "", editorial_note).strip()
    if curation == "curated_sectioned" and section_count > 0:
        suffix = f"source-section pass 2026-07-09 ({section_count} sections)."
        return f"{cleaned} - {suffix}" if cleaned else suffix
    return cleaned


def retrofit_source(
    path: Path,
    since_date: str,
    until_date: str | None = None,
    dry_run: bool = False,
    force_sections: bool = False,
    sectioning: str = "auto",
) -> str | None:
    try:
        path_label = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        path_label = path.as_posix()
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter_lines = parts[1].splitlines()
    frontmatter = parse_frontmatter_lines(frontmatter_lines)
    host_slug = unquote_scalar(frontmatter.get("host_slug", "")) or unquote_scalar(frontmatter.get("channel_slug", ""))
    if not host_slug and path.name.startswith("source-alexander-mercouris-"):
        host_slug = "alexander-mercouris"
    pub_date = unquote_scalar(frontmatter.get("pub_date", ""))
    if not host_slug or pub_date < since_date or (until_date and pub_date > until_date):
        return None
    split = split_source_document(text)
    if split is None:
        return f"SKIP malformed {path_label}"

    _, body_prefix, body = split

    args = SimpleNamespace(
        host_slug=host_slug,
        trim_opening="auto",
        asr_repair="auto",
        opening_trim_applied=unquote_scalar(frontmatter.get("opening_trim_applied", "false")) == "true",
        opening_trim_rule=unquote_scalar(frontmatter.get("opening_trim_rule", "")),
        opening_trim_chars_saved=safe_int(frontmatter.get("opening_trim_chars_saved", "0")),
        opening_trim_words_saved=safe_int(frontmatter.get("opening_trim_words_saved", "0")),
        closing_trim_applied=unquote_scalar(frontmatter.get("closing_trim_applied", "false")) == "true",
        closing_trim_rule=unquote_scalar(frontmatter.get("closing_trim_rule", "")),
        closing_trim_chars_saved=safe_int(frontmatter.get("closing_trim_chars_saved", "0")),
        closing_trim_words_saved=safe_int(frontmatter.get("closing_trim_words_saved", "0")),
        asr_repair_applied=unquote_scalar(frontmatter.get("asr_repair_applied", "false")) == "true",
        asr_repair_pass=unquote_scalar(frontmatter.get("asr_repair_pass", "")),
        title=unquote_scalar(frontmatter.get("title", path.stem)),
        source_form=unquote_scalar(frontmatter.get("source_form", "interview")),
        sectioning=sectioning,
        transcript_curation="preserved_unsectioned",
        section_count=0,
        section_pass=SECTIONING_PASS_LABEL,
        editorial_note=unquote_scalar(frontmatter.get("editorial_note", "")),
    )
    original_section_count = len(re.findall(r"(?m)^### ", body))
    existing_curation = unquote_scalar(frontmatter.get("transcript_curation", ""))
    trimmed_body = body
    if host_slug in HOST_TRIM_RULES:
        trimmed_body = apply_trim_metadata(args, body)
    repaired_body = repair_asr_text(args, normalize_inline_turn_markers(trimmed_body))
    section_body = repaired_body
    if not force_sections and (existing_curation == "curated_sectioned" or original_section_count > 0):
        args.transcript_curation = "curated_sectioned"
        args.section_count = original_section_count
    else:
        base_body = strip_transcript_section_headings(repaired_body) if force_sections else repaired_body
        section_body, args.transcript_curation, args.section_count, _ = section_transcript(args, base_body)
    args.editorial_note = update_editorial_note(args.editorial_note, args.transcript_curation, args.section_count)
    new_frontmatter_lines = normalize_frontmatter_trim_fields(frontmatter_lines, args, section_body)
    new_text = "---\n" + "\n".join(new_frontmatter_lines) + "\n---" + body_prefix + section_body.rstrip() + "\n"

    body_changed = section_body != body
    metadata_changed = new_frontmatter_lines != frontmatter_lines
    if not body_changed and not metadata_changed:
        return f"UNCHANGED {path_label}"

    if not dry_run:
        path.write_text(new_text, encoding="utf-8", newline="\n")

    if body_changed:
        return (
            f"TRIMMED {path_label} "
            f"opening={args.opening_trim_chars_saved} closing={args.closing_trim_chars_saved} sections={args.section_count}"
        )
    return f"NORMALIZED {path_label}"


def backfill_sources(
    since_date: str,
    until_date: str | None = None,
    dry_run: bool = False,
    force_sections: bool = False,
    sectioning: str = "auto",
) -> list[str]:
    since_date = validate_iso_date(since_date, "backfill_since")
    if until_date is not None:
        until_date = validate_iso_date(until_date, "backfill_until")
        if until_date < since_date:
            raise ValueError("backfill_until must not be earlier than backfill_since")
    if not dry_run:
        raise ValueError(
            "Legacy backfill execution is disabled; use tools/run.ps1 archive-repair "
            "with an explicit class, target set, and reviewed plan digest."
        )
    messages: list[str] = []
    for path in sorted(ARCHIVE_SOURCES_ROOT.rglob("source-*.md")):
        result = retrofit_source(
            path,
            since_date,
            until_date=until_date,
            dry_run=dry_run,
            force_sections=force_sections,
            sectioning=sectioning,
        )
        if result:
            messages.append(result)
    return messages


def source_plan(args: SimpleNamespace) -> tuple[Path, str, str]:
    title_core_slug = slugify(args.title)
    if not title_core_slug:
        raise ValueError("title must contain at least one letter or number")
    file_slug = f"source-{title_core_slug}-{args.pub_date}.md"
    title_slug = f"transcript-{title_core_slug}-{args.pub_date}"
    day_dir = ARCHIVE_SOURCES_ROOT / args.pub_date
    source_path = day_dir / file_slug
    expected_parent = day_dir.resolve()
    sources_root = ARCHIVE_SOURCES_ROOT.resolve()
    if expected_parent.parent != sources_root or source_path.resolve().parent != expected_parent:
        raise ValueError("generated source path must stay under archive/sources/geopolitics/sources/YYYY-MM-DD")
    upstream_path = args.upstream_path or f"operator-paste://{args.ingest_date}/{title_core_slug}"
    return source_path, title_slug, upstream_path


def prepare_landing(args: SimpleNamespace) -> LandingPlan:
    if getattr(args, "body_file", None):
        body_path = Path(args.body_file)
        if not body_path.is_file():
            raise FileNotFoundError(f"Body file not found: {body_path}")

    source_path, title_slug, upstream_path = source_plan(args)
    body = load_body_text(args)
    body = apply_trim_metadata(args, body)
    body = normalize_inline_turn_markers(body)
    body = repair_asr_text(args, body)
    body, args.transcript_curation, args.section_count, _ = section_transcript(args, body)
    args.editorial_note = update_editorial_note(args.editorial_note, args.transcript_curation, args.section_count)
    frontmatter_doc = build_frontmatter(args, title_slug, body)
    manifest_row = build_manifest_row(args, source_path, upstream_path)
    return LandingPlan(source_path, frontmatter_doc, manifest_row)


def prepare_batch(source_args: list[SimpleNamespace], manifest: dict) -> tuple[list[LandingPlan], dict]:
    manifest_sources = manifest.get("sources")
    if not isinstance(manifest_sources, list):
        raise ValueError("Manifest format error: 'sources' is not a list.")
    existing_path_list = [
        item.get("local_path")
        for item in manifest_sources
        if isinstance(item, dict) and item.get("local_path")
    ]
    if len(existing_path_list) != len(set(existing_path_list)):
        raise ValueError("Manifest contains duplicate source paths")
    existing_paths = set(existing_path_list)
    existing_identities = {
        str(item.get("source_identity") or "").strip()
        for item in manifest_sources
        if isinstance(item, dict) and item.get("source_identity")
    }
    existing_identities.update(archived_source_identities())
    existing_urls = {
        str(item.get("url") or item.get("source_url") or "").strip().rstrip("/")
        for item in manifest_sources
        if isinstance(item, dict) and (item.get("url") or item.get("source_url"))
    }
    plans: list[LandingPlan] = []
    planned_paths: set[str] = set()
    for args in source_args:
        plan = prepare_landing(args)
        if args.source_identity and args.source_identity in existing_identities:
            raise ValueError(f"Source identity already exists in manifest: {args.source_identity}")
        if args.url and args.url.rstrip("/") in existing_urls:
            raise ValueError(f"Source URL already exists in manifest: {args.url}")
        relative_path = plan.source_path.relative_to(REPO_ROOT).as_posix()
        if relative_path in existing_paths:
            raise ValueError(f"Manifest already contains source path: {relative_path}")
        if relative_path in planned_paths:
            raise ValueError(f"Batch contains duplicate source path: {relative_path}")
        if plan.source_path.exists():
            raise FileExistsError(f"Refusing to overwrite existing source file: {relative_path}")
        planned_paths.add(relative_path)
        plans.append(plan)
    proposed = copy.deepcopy(manifest)
    proposed_sources = proposed["sources"]
    proposed_sources.extend(copy.deepcopy(plan.manifest_row) for plan in plans)
    proposed["source_count"] = len(proposed_sources)
    manifest_bytes(proposed)
    return plans, proposed


def preflight_receipt(source_args: list[SimpleNamespace], manifest: dict) -> dict[str, object]:
    sources = manifest.get("sources", [])
    existing = [item for item in sources if isinstance(item, dict)]
    identities = {str(item.get("source_identity") or "") for item in existing}
    urls = {str(item.get("source_url") or item.get("url") or "").rstrip("/") for item in existing}
    archived_identities = archived_source_identities()
    rows: list[dict[str, object]] = []
    for args in sorted(source_args, key=lambda item: (item.pub_date, item.title, item.source_identity)):
        source_path, _, _ = source_plan(args)
        identity_duplicate = bool(args.source_identity and (args.source_identity in identities or args.source_identity in archived_identities))
        url_duplicate = bool(args.url and args.url.rstrip("/") in urls)
        warnings = list(getattr(args, "metadata_warnings", []))
        if identity_duplicate or url_duplicate:
            warnings.append("already-landed-identity")
        rows.append({
            "video_id": youtube_video_id(args.url),
            "source_identity": args.source_identity,
            "duplicate": identity_duplicate or url_duplicate,
            "planned_path": source_path.relative_to(REPO_ROOT).as_posix(),
            "title": args.title,
            "title_source": args.title_source,
            "title_aliases": args.title_aliases,
            "date": args.pub_date,
            "date_basis": args.date_basis,
            "host": args.host,
            "host_slug": args.host_slug,
            "guest": args.guest,
            "voice_slugs": args.voice_slugs,
            "source_form": args.source_form,
            "source_form_basis": args.source_form_basis,
            "transformations": [name for name, applied in (("opening-trim", args.opening_trim_applied), ("closing-trim", args.closing_trim_applied), ("asr-repair", args.asr_repair_applied), ("sectioning", args.transcript_curation == "curated_sectioned")) if applied],
            "warnings": warnings,
        })
    warning_events = sum(len(row["warnings"]) for row in rows)
    warning_sources = sum(bool(row["warnings"]) for row in rows)
    duplicate_stops = sum(bool(row["duplicate"]) for row in rows)
    correction_signal_events = sum(
        len(row["title_aliases"])
        + sum(warning != "already-landed-identity" for warning in row["warnings"])
        for row in rows
    )
    correction_signal_sources = sum(
        bool(row["title_aliases"])
        or any(warning != "already-landed-identity" for warning in row["warnings"])
        for row in rows
    )
    metrics = {
        "disposition": "preflight-only",
        "attempted_sources": len(rows),
        "warning_sources": warning_sources,
        "warning_events": warning_events,
        "duplicate_stops": duplicate_stops,
        "correction_signal_sources": correction_signal_sources,
        "correction_signal_events": correction_signal_events,
        "successful_landings": 0,
        "failed_attempts": 0,
    }
    return {
        "status": "warning" if warning_sources else "ready",
        "count": len(rows),
        "sources": rows,
        "outcome_metrics": metrics,
    }


def disposition_metrics(
    receipt: dict[str, object],
    disposition: str,
    *,
    successful_landings: int = 0,
    failed_attempts: int = 0,
) -> dict[str, object]:
    metrics = dict(receipt.get("outcome_metrics", {}))
    metrics.update(
        {
            "disposition": disposition,
            "successful_landings": successful_landings,
            "failed_attempts": failed_attempts,
        }
    )
    return metrics


def dry_run_messages(plans: list[LandingPlan]) -> list[str]:
    return [
        f"DRY RUN: {plan.source_path.relative_to(REPO_ROOT).as_posix()}\n"
        f"{json.dumps(plan.manifest_row, indent=2)}"
        for plan in plans
    ]


def stage_bytes(path: Path, payload: bytes) -> Path:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".stage", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def publish_batch(
    plans: list[LandingPlan],
    manifest: dict,
    voice_updates: dict[Path, str] | None = None,
) -> list[str]:
    voice_updates = voice_updates or {}
    staged_sources: list[tuple[Path, Path]] = []
    staged_indexes: list[tuple[Path, Path]] = []
    original_indexes: dict[Path, bytes] = {}
    published_sources: list[Path] = []
    published_indexes: list[Path] = []
    created_directories: list[Path] = []
    staged_manifest: Path | None = None
    manifest_published = False
    try:
        for plan in plans:
            parent = plan.source_path.parent
            if not parent.exists():
                parent.mkdir(parents=True)
                created_directories.append(parent)
            staged_sources.append(
                (
                    stage_bytes(plan.source_path, plan.source_text.encode("utf-8")),
                    plan.source_path,
                )
            )
        for target, rendered in sorted(voice_updates.items(), key=lambda item: str(item[0])):
            original_indexes[target] = target.read_bytes()
            staged_indexes.append(
                (stage_bytes(target, rendered.encode("utf-8")), target)
            )
        staged_manifest = stage_bytes(MANIFEST_PATH, manifest_bytes(manifest))
        for staged, target in staged_sources:
            if target.exists():
                raise FileExistsError(
                    "Refusing to overwrite existing source file: "
                    f"{target.relative_to(REPO_ROOT).as_posix()}"
                )
            os.replace(staged, target)
            published_sources.append(target)
        for staged, target in staged_indexes:
            os.replace(staged, target)
            published_indexes.append(target)
        os.replace(staged_manifest, MANIFEST_PATH)
        manifest_published = True
    except BaseException:
        if not manifest_published:
            for target in reversed(published_indexes):
                target.write_bytes(original_indexes[target])
            for target in reversed(published_sources):
                target.unlink(missing_ok=True)
        raise
    finally:
        for staged, _ in staged_sources:
            staged.unlink(missing_ok=True)
        for staged, _ in staged_indexes:
            staged.unlink(missing_ok=True)
        if staged_manifest is not None:
            staged_manifest.unlink(missing_ok=True)
        if not manifest_published:
            for directory in reversed(created_directories):
                try:
                    directory.rmdir()
                except OSError:
                    pass
    return [
        f"Landed source: {plan.source_path.relative_to(REPO_ROOT).as_posix()}"
        for plan in plans
    ]


def project_voice_indexes_for_plans(
    plans: list[LandingPlan], manifest: dict
) -> tuple[dict[Path, str], list[str]]:
    run_dates = sorted(
        {
            str(plan.manifest_row.get("date", ""))
            for plan in plans
            if plan.manifest_row.get("date")
        }
    )
    updates: dict[Path, str] = {}
    changed_shelves: set[str] = set()
    added_routes: set[str] = set()
    unindexed_voices: set[str] = set()
    failures: list[str] = []
    for run_date in run_dates:
        projected, report = voice_indexes.project(
            manifest,
            run_date=run_date,
            repo_root=REPO_ROOT,
            voices_root=NG_ROOT / "voices",
        )
        updates.update(projected)
        changed_shelves.update(report.get("changed_shelves", []))
        added_routes.update(report.get("added_routes", []))
        unindexed_voices.update(report.get("unindexed_voices", []))
        failures.extend(report.get("failures", []))
    repairable = (
        "manifest route missing voice shelf:",
        "stale voice corpus count:",
        "duplicate voice route:",
    )
    planned_missing = {
        f"missing archive source file: {plan.manifest_row['local_path']}"
        for plan in plans
    }
    failures = [
        item
        for item in failures
        if not item.startswith(repairable) and item not in planned_missing
    ]
    if failures:
        raise ValueError("Voice index projection failed:\n" + "\n".join(sorted(set(failures))))
    messages: list[str] = []
    if changed_shelves:
        messages.append(f"Voice shelves changed: {', '.join(sorted(changed_shelves))}")
    if added_routes:
        messages.append(f"Voice routes added: {len(added_routes)}")
    if unindexed_voices:
        messages.append(f"Unindexed voices: {', '.join(sorted(unindexed_voices))}")
    return updates, messages


def sync_voice_indexes_for_plans(plans: list[LandingPlan], manifest: dict) -> list[str]:
    run_dates = sorted(
        {
            str(plan.manifest_row.get("date", ""))
            for plan in plans
            if plan.manifest_row.get("date")
        }
    )
    changed_shelves: set[str] = set()
    added_routes: set[str] = set()
    unindexed_voices: set[str] = set()
    failures: list[str] = []

    for run_date in run_dates:
        report = voice_indexes.reconcile(
            manifest,
            run_date=run_date,
            write=True,
            repo_root=REPO_ROOT,
            voices_root=NG_ROOT / "voices",
        )
        changed_shelves.update(report.get("changed_shelves", []))
        added_routes.update(report.get("added_routes", []))
        unindexed_voices.update(report.get("unindexed_voices", []))
        failures.extend(report.get("failures", []))

    if failures:
        unique_failures = "\n".join(sorted(set(failures)))
        raise ValueError(f"Voice index sync failed:\n{unique_failures}")

    messages = []
    if changed_shelves:
        messages.append(f"Voice shelves changed: {', '.join(sorted(changed_shelves))}")
    if added_routes:
        messages.append(f"Voice routes added: {len(added_routes)}")
    if unindexed_voices:
        messages.append(f"Unindexed voices: {', '.join(sorted(unindexed_voices))}")
    return messages


def metadata_files_from_batch_dir(batch_dir: Path) -> list[Path]:
    if not batch_dir.is_dir():
        raise NotADirectoryError(f"Batch directory not found: {batch_dir}")
    files = [
        path
        for path in sorted(batch_dir.iterdir())
        if path.is_file() and path.suffix.lower() in METADATA_SUFFIXES
    ]
    if not files:
        raise FileNotFoundError(f"No metadata sidecars found in: {batch_dir}")
    return files


def gather_sources(cli_args: argparse.Namespace) -> list[SimpleNamespace]:
    if cli_args.quick and cli_args.batch_dir:
        batch_dir = Path(cli_args.batch_dir)
        if not batch_dir.is_dir():
            raise FileNotFoundError(f"Quick batch directory not found: {batch_dir}")
        body_files = sorted(
            path for path in batch_dir.iterdir()
            if path.is_file() and path.suffix.lower() in METADATA_SUFFIXES
        )
        if not body_files:
            raise ValueError(f"Quick batch directory contains no {METADATA_SUFFIXES} body files: {batch_dir}")
        sources: list[SimpleNamespace] = []
        for body_file in body_files:
            args = args_from_cli(cli_args, normalize=False)
            args.body_file = str(body_file)
            args.body_text = ""
            args.title = ""
            args.url = ""
            args.quick_positionals = []
            sources.append(normalize_args(args))
        return sources
    mode_count = sum(bool(item) for item in (cli_args.metadata_file, cli_args.batch_dir))
    if mode_count > 1:
        raise ValueError("Choose only one of --metadata-file or --batch-dir.")

    if cli_args.batch_dir:
        batch_dir = Path(cli_args.batch_dir)
        return [
            args_from_metadata(parse_metadata_file(path), path, cli_args)
            for path in metadata_files_from_batch_dir(batch_dir)
        ]

    if cli_args.metadata_file:
        metadata_path = Path(cli_args.metadata_file)
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        return [args_from_metadata(parse_metadata_file(metadata_path), metadata_path, cli_args)]

    return [args_from_cli(cli_args)]


def main() -> int:
    cli_args = parse_args()
    receipt: dict[str, object] | None = None

    try:
        if cli_args.backfill_since:
            messages = backfill_sources(
                cli_args.backfill_since,
                until_date=cli_args.backfill_until,
                dry_run=cli_args.dry_run,
                force_sections=cli_args.force_sections,
                sectioning=cli_args.sectioning,
            )
            print("\n".join(messages))
            return 0
        source_args = gather_sources(cli_args)
        manifest = load_manifest()
        receipt = preflight_receipt(source_args, manifest)
        if cli_args.preflight:
            print(json.dumps(receipt, indent=2, ensure_ascii=False) if cli_args.json else json.dumps(receipt, indent=2, ensure_ascii=False))
            return 0
        existing_urls = archived_source_urls()
        existing_identities = archived_source_identities()
        if len(source_args) == 1 and source_args[0].source_identity in existing_identities:
            result = {
                "status": "ALREADY LANDED",
                "archive": existing_identities[source_args[0].source_identity],
                "source_identity": source_args[0].source_identity,
                "preflight": receipt,
                "outcome_metrics": disposition_metrics(receipt, "duplicate-prevented"),
            }
            print(json.dumps(result, indent=2) if cli_args.json else f"ALREADY LANDED\nArchive: {result['archive']}")
            return 0
        matching_url_path = next((path for url, path in existing_urls.items() if url.rstrip("/") == source_args[0].url.rstrip("/")), None)
        if len(source_args) == 1 and matching_url_path:
            result = {
                "status": "ALREADY LANDED",
                "archive": matching_url_path,
                "source_identity": source_args[0].source_identity,
                "preflight": receipt,
                "outcome_metrics": disposition_metrics(receipt, "duplicate-prevented"),
            }
            print(json.dumps(result, indent=2) if cli_args.json else f"ALREADY LANDED\nArchive: {result['archive']}")
            return 0
        plans, proposed_manifest = prepare_batch(source_args, manifest)
        if cli_args.dry_run:
            messages = dry_run_messages(plans)
        else:
            voice_updates, voice_messages = project_voice_indexes_for_plans(
                plans, proposed_manifest
            )
            messages = publish_batch(plans, proposed_manifest, voice_updates)
            messages.extend(voice_messages)
            messages.append(f"Manifest count: {proposed_manifest['source_count']}")
        if receipt.get("status") == "warning":
            messages.insert(0, f"Preflight: WARNING ({sum(bool(row['warnings']) for row in receipt['sources'])} source(s))")
        if cli_args.json:
            disposition = "dry-run" if cli_args.dry_run else "landed"
            result = {
                "status": disposition,
                "preflight": receipt,
                "outcome_metrics": disposition_metrics(
                    receipt,
                    disposition,
                    successful_landings=0 if cli_args.dry_run else len(plans),
                ),
                "messages": messages,
            }
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n".join(messages))
        return 0
    except Exception as exc:  # noqa: BLE001
        if cli_args.json and receipt is not None:
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "error": str(exc),
                        "preflight": receipt,
                        "outcome_metrics": disposition_metrics(
                            receipt, "failed", failed_attempts=1
                        ),
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
        else:
            print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
