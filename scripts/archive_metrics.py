"""Read-only archive metrics backed by the collection-aware query substrate."""
from __future__ import annotations
import argparse, json, statistics
from collections import Counter
try:
    from archive_query import query_snapshot, is_transcript_modality
except ModuleNotFoundError:
    from scripts.archive_query import query_snapshot, is_transcript_modality

def load_metrics(month=None, collections=("geopolitics",), channels=(), transcript_only=False, curated_channels=False):
    snapshot = query_snapshot(collections, month, channels, transcript_only, curated_channels)
    rows = snapshot["records"]
    daily = Counter(str(row.get("date", row.get("publication_date"))) for row in rows if is_transcript_modality(row.get("modality", row.get("kind", row.get("document_type")))))
    counts = list(daily.values())
    result = {"scope": month or "all", "collections": snapshot["collections"], "roster_source": "geopolitics/channels/channel-index.md" if snapshot["roster"] else None, "channel_results": snapshot.get("channel_results", []), "predicate": "transcript-qualified modality; collection-native kind/document_type fallback", "manifest_rows": len(rows), "transcript_like_rows": sum(daily.values()), "modality_distribution": dict(sorted(Counter(str(r.get("modality", r.get("kind", r.get("document_type") or "unknown"))) for r in rows).items())), "daily_transcript_counts": dict(sorted(daily.items())), "warnings": snapshot["warnings"], "status": "incomplete" if snapshot["warnings"] else "complete"}
    if snapshot["collections"] and snapshot["collections"][0].get("parity"):
        result["parity"] = snapshot["collections"][0]["parity"]
    result["daily_statistics"] = {"populated_days": len(counts), "mean": round(statistics.mean(counts), 2) if counts else 0, "median": statistics.median(counts) if counts else 0, "min": min(counts) if counts else 0, "max": max(counts) if counts else 0}
    return result

def main():
    p=argparse.ArgumentParser(description="Collection-aware read-only archive metrics")
    p.add_argument("--month"); p.add_argument("--collection", action="append", dest="collections"); p.add_argument("--channel", action="append", default=[]); p.add_argument("--transcript-only", action="store_true"); p.add_argument("--curated-channels", action="store_true"); p.add_argument("--json", action="store_true"); a=p.parse_args()
    try: result=load_metrics(a.month, tuple(a.collections or ("geopolitics",)), a.channel, a.transcript_only, a.curated_channels)
    except (OSError, json.JSONDecodeError, ValueError) as error: print(f"archive metrics failed: {error}"); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2) if a.json else f"scope={result['scope']}\nstatus={result['status']}\ntranscript_like_rows={result['transcript_like_rows']}\nstatistics={json.dumps(result['daily_statistics'])}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
