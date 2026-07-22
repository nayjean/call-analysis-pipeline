import json
import os

import pandas as pd
import streamlit as st

RESULTS_FOLDER = "output/results"

st.title("Call Analysis Dashboard")


def load_results():
    rows = []
    result_files = [f for f in os.listdir(RESULTS_FOLDER) if f.endswith(".json")]

    for filename in result_files:
        with open(os.path.join(RESULTS_FOLDER, filename), "r", encoding="utf-8") as file:
            data = json.load(file)

        summary = data["summary"]
        call_id = filename.replace(".json", "")

        if summary.get("status") == "no_speech_detected":
            rows.append({
                "call_id": call_id,
                "status": "no speech detected",
                "trend": None,
                "sentiment": None,
                "intent": None,
                "escalation_level": None,
                "escalation_score": None
            })
            continue

        rows.append({
            "call_id": call_id,
            "status": "ok",
            "trend": summary["trend"],
            "sentiment": round(summary["overall_average_sentiment"], 2),
            "intent": summary["intent"]["trusted_intent"],
            "escalation_level": summary["escalation"]["escalation_level"],
            "escalation_score": summary["escalation"]["escalation_score"]
        })

    return pd.DataFrame(rows)


df = load_results()
answered_df = df[df["status"] == "ok"]

st.subheader(f"All Calls ({len(df)} total)")
st.dataframe(df)

col1, col2, col3 = st.columns(3)
col1.metric("Total Calls", len(df))
col2.metric("Analyzed Calls", len(answered_df))
col3.metric("No Speech Detected", len(df) - len(answered_df))

st.subheader("Escalation Levels")
st.bar_chart(answered_df["escalation_level"].value_counts())

st.subheader("Intent Distribution")
st.bar_chart(answered_df["intent"].value_counts())

st.subheader("Sentiment Trend Distribution")
st.bar_chart(answered_df["trend"].value_counts())

st.subheader("Escalation Hotlist (Medium/High)")
hotlist = answered_df[answered_df["escalation_level"].isin(["Medium", "High"])]
if len(hotlist) == 0:
    st.write("No calls currently flagged for escalation review.")
else:
    st.dataframe(hotlist[["call_id", "escalation_level", "escalation_score", "intent", "sentiment"]])
