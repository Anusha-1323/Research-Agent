import plotly.express as px


def ats_pie_chart(df):

    return px.pie(
        df,
        names="Resume",
        values="ATS Score",
        title="ATS Score Comparison"
    )


def ats_bar_chart(df):

    return px.bar(
        df,
        x="Resume",
        y="ATS Score",
        text="ATS Score",
        title="ATS Score Comparison"
    )