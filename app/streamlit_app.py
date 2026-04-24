import streamlit as st
import sys
import os
sys.path.insert(0, os.getcwd())
from app.classifier import classify_message
from app.schemas import MessageInput

st.set_page_config(page_title="Clinic Inbox Triage", layout="centered")
st.title("Clinic Inbox Triage Assistant")
st.markdown("Classify incoming patient messages and surface urgent cases immediately.")
st.divider()
message_text = st.text_area("Patient Message", placeholder="Paste or type the patient message here...", height=150)
message_id = st.text_input("Message ID", value="msg_001")
if st.button("Classify Message", type="primary"):
    if not message_text.strip():
        st.warning("Please enter a message to classify.")
    else:
        with st.spinner("Classifying..."):
            try:
                result = classify_message(MessageInput(id=message_id, text=message_text))
                severity = result.severity.value
                label = result.primary_label.value.replace("_", " ").upper()
                if severity == "high":
                    st.error(f"URGENT: {label}")
                elif severity == "medium":
                    st.warning(f"REVIEW NEEDED: {label}")
                else:
                    st.success(f"ROUTINE: {label}")
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Severity", severity.upper())
                    st.metric("Confidence", f"{result.confidence:.0%}")
                with col2:
                    st.metric("Primary Label", result.primary_label.value)
                    if result.secondary_label:
                        st.metric("Secondary Label", result.secondary_label.value)
                st.divider()
                st.subheader("Recommended Action")
                st.info(result.recommended_action)
                st.subheader("Safe Draft Reply")
                st.text_area("Copy this reply:", value=result.safe_reply, height=100)
                st.subheader("Reasoning Tags")
                st.write(" | ".join(result.reasoning_tags))
                if result.policy_override_triggered:
                    st.divider()
                    st.caption("Policy override was triggered on this message.")
            except Exception as e:
                st.error(f"Classification failed: {str(e)}")
st.divider()
st.caption("Clinic Inbox Triage Assistant v1.0 - All urgent classifications require human review.")
