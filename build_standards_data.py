import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "Social Studies": Path(r"C:\Users\patri\Downloads\Kentucky_Academic_Standards_for_Social_Studies.pdf"),
    "English Language Arts": Path(r"C:\Users\patri\Downloads\Kentucky_Academic_Standards_for_Reading_and_Writing_2025.pdf"),
    "Science": Path(r"C:\Users\patri\Downloads\Kentucky_Academic_Standards_for_Science_2022.pdf"),
    "Mathematics": Path(r"C:\Users\patri\Downloads\Kentucky_Academic_Standards_Mathematics.pdf"),
}


def compact(value):
    value = value.replace("\u00ad", "").replace("\uf0b7", "•")
    value = re.sub(r"\s+", " ", value)
    return value.strip(" \t\r\n-–—:;")


def fix_spacing_artifacts(value):
    replacements = {
        "anal yze": "analyze",
        "ca use": "cause",
        "comm unities": "communities",
        "de mocratic": "democratic",
        "develo pment": "development",
        "gover nment": "government",
        "inc entives": "incentives",
        "int eractions": "interactions",
        "peopl e": "people",
        "physi cal": "physical",
        "pur pose": "purpose",
        "re sponsibilities": "responsibilities",
        "res ponsibilities": "responsibilities",
        "respo nsibilities": "responsibilities",
        "whe ther": "whether",
        "whethe r": "whether",
    }
    for bad, good in replacements.items():
        value = re.sub(re.escape(bad), good, value, flags=re.I)
    return value


def trim_at(value, markers):
    end = len(value)
    for marker in markers:
        index = value.find(marker)
        if index >= 0:
            end = min(end, index)
    return compact(value[:end])


def first_sentence(value):
    match = re.search(r"(?<!U\.S)(?<!e\.g)(?<!Nos)\.(?=\s+[A-Z])", value)
    if match:
        return compact(value[: match.end()])
    return compact(value)


def grade_values(token):
    token = token.upper().replace("–", "-")
    if token == "K":
        return ["K"]
    if token == "HS":
        return ["9", "10", "11", "12"]
    if "-" in token:
        start, end = token.split("-", 1)
        start_value = 0 if start == "K" else int(start)
        end_value = int(end)
        return ["K" if value == 0 else str(value) for value in range(start_value, end_value + 1)]
    return [token]


def add_candidate(candidates, code, description, priority=0):
    description = compact(description)
    description = fix_spacing_artifacts(description)
    description = re.sub(r"\s+([,.;:!?])", r"\1", description)
    description = re.sub(r"\((?:content|analysis|comprehension)\)", "", description, flags=re.I)
    description = compact(description)
    if len(description) < 12 or len(description) > 1800:
        return
    if "→" in description or description.lower().startswith("coherence"):
        return
    candidates[code].append((priority, description))


def best_candidates(candidates):
    chosen = {}
    for code, values in candidates.items():
        def score(item):
            priority, text = item
            sentence_bonus = 100 if text.endswith((".", "?", "!")) else 0
            natural_bonus = 80 if not re.search(r"\b[A-Z]{4,}\b", text) else 0
            return priority * 10000 + sentence_bonus + natural_bonus + min(len(text), 900)

        chosen[code] = max(values, key=score)[1]
    return chosen


def parse_math(path):
    candidates = defaultdict(list)
    code_re = re.compile(r"\bKY\.(?:K|[1-8]|HS)\.[A-Z][A-Z0-9]*\.\d+[a-z]?\b")
    for page in PdfReader(str(path)).pages:
        text = compact(page.extract_text() or "")
        matches = list(code_re.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            candidate = text[match.end():end]
            candidate = trim_at(candidate, [" MP.1", " MP.2", " MP.3", " MP.4", " MP.5", " MP.6", " MP.7", " MP.8", " Coherence", " Attending to", " Standards Clarifications"])
            candidate = re.sub(r"^\s*\(\+{1,2}\)\s*", "", candidate)
            add_candidate(candidates, match.group(), candidate, 2)
    return best_candidates(candidates)


def parse_science(path):
    candidates = defaultdict(list)
    code_re = re.compile(r"\b(?:K|[1-8]|K-2|3-5|6-8|HS)-(?:PS|LS|ESS|ETS)\d+-\d+\b")
    for page in PdfReader(str(path)).pages:
        text = compact(page.extract_text() or "")
        matches = list(code_re.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            candidate = text[match.end():end].lstrip(". ")
            candidate = trim_at(candidate, [" Clarification Statement", " Assessment Boundary", " The performance expectation", " Connections to other", " Foundation Boxes"])
            add_candidate(candidates, match.group(), candidate, 3)
    return best_candidates(candidates)


def parse_social_studies(path):
    candidates = defaultdict(list)
    code_re = re.compile(r"\b(?:K|[1-8]|HS)\.[CEGHI]\.[A-Z]{1,4}\.\d+\b")
    for page in PdfReader(str(path)).pages:
        text = compact(page.extract_text() or "")
        matches = list(code_re.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            candidate = text[match.end():end]
            candidate = trim_at(candidate, [" Disciplinary Clarifications", " Inquiry Practices", " Supporting Question", " Disciplinary Concept", " Sample Compelling"])
            candidate = first_sentence(candidate)
            add_candidate(candidates, match.group(), candidate, 2)
    return best_candidates(candidates)


def parse_ela(path):
    candidates = defaultdict(list)
    code_re = re.compile(r"\b(?:RL|RI|C|L|RF|HW)\.(?:K|[1-8]|9[-–]10|11[-–]12)\.\d+[a-z]?\b")
    title_re = re.compile(
        r"(Reading Literature|Reading Informational Text|Composition|Language|Reading Foundational Skills|Handwriting), "
        r"(Kindergarten|Grade [1-8]|Grades 9[-–]10|Grades 11[-–]12), Standard (\d+)"
    )
    strand_codes = {
        "Reading Literature": "RL",
        "Reading Informational Text": "RI",
        "Composition": "C",
        "Language": "L",
        "Reading Foundational Skills": "RF",
        "Handwriting": "HW",
    }
    for page in PdfReader(str(path)).pages:
        text = compact(page.extract_text() or "")

        for title in title_re.finditer(text):
            grade_label = title.group(2)
            grade = "K" if grade_label == "Kindergarten" else grade_label.replace("Grade ", "").replace("Grades ", "").replace("–", "-")
            code = f"{strand_codes[title.group(1)]}.{grade}.{title.group(3)}"
            start = text.find("Multidimensionality", title.end())
            if start >= 0:
                start += len("Multidimensionality")
                following = code_re.search(text, start)
                end = following.start() if following else len(text)
                candidate = trim_at(text[start:end], [
                    " Progression", " Guiding Principle", " Production and Distribution",
                    " Reading Literature,", " Reading Informational Text,", " Composition, Grade",
                    " Language, Grade", " Reading Foundational Skills,", " Handwriting, Grade",
                ])
                add_candidate(candidates, code, candidate, 4)

        matches = list(code_re.finditer(text))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            candidate = text[match.end():end]
            candidate = trim_at(candidate, [" Guiding Principle", " Progression", " Multidimensionality", " Kentucky Academic Standards"])
            if not candidate.lower().startswith("no "):
                add_candidate(candidates, match.group().replace("–", "-"), candidate, 2)
    return best_candidates(candidates)


def grade_token(subject, code):
    if subject == "Mathematics":
        return code.split(".")[1]
    if subject == "English Language Arts":
        return code.split(".")[1]
    if subject == "Science":
        return code.split("-", 1)[0]
    return code.split(".", 1)[0]


def main():
    parsers = {
        "Social Studies": parse_social_studies,
        "English Language Arts": parse_ela,
        "Science": parse_science,
        "Mathematics": parse_math,
    }
    records = []
    counts = {}

    for subject, path in SOURCES.items():
        parsed = parsers[subject](path)
        parsed = {code: text for code, text in parsed.items() if not text.lower().startswith("begins in grade")}
        counts[subject] = len(parsed)
        for code, text in parsed.items():
            for grade in grade_values(grade_token(subject, code)):
                records.append({
                    "code": code,
                    "subject": subject,
                    "grade": grade,
                    "text": text,
                })

    grade_order = {"K": 0, **{str(value): value for value in range(1, 13)}}
    records.sort(key=lambda item: (grade_order.get(item["grade"], 99), item["subject"], item["code"]))

    (ROOT / "standards.json").write_text(json.dumps(records, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    js = "window.BELLRINGER_STANDARDS = " + json.dumps(records, ensure_ascii=True, separators=(",", ":")) + ";\n"
    (ROOT / "standards-data.js").write_text(js, encoding="utf-8")

    print(json.dumps({"unique_codes": counts, "app_records": len(records)}, indent=2))
    for grade in ["K", "5", "6", "7", "8", "12"]:
        grade_records = [item for item in records if item["grade"] == grade]
        print(f"Grade {grade}: {len(grade_records)} records")


if __name__ == "__main__":
    main()
