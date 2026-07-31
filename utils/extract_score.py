import re

def extract_score(report):

    match = re.search(r"ATS Score[:\s]*([0-9]+)", report, re.IGNORECASE)

    if match:
        return int(match.group(1))

    return 0