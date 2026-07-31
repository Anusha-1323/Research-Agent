import pandas as pd


def create_comparison_table(ats_reports, extract_score):

    rows = []

    for name, report in ats_reports.items():

        rows.append(
            {
                "Resume": name,
                "ATS Score": extract_score(report)
            }
        )

    df = pd.DataFrame(rows)

    if not df.empty:
        df = df.sort_values(
            "ATS Score",
            ascending=False
        )

    return df