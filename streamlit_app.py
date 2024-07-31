import os
from dotenv import load_dotenv
import streamlit as st
import llm
import base64
import json
import time


load_dotenv()

st.header("Generate Question and Answers for Learning Unit", anchor=None, help=None, divider="blue")

file = st.file_uploader("Upload Unit document here", type=['pdf'], accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")

if file is not None:
    # st.text(file)
    if file.type == "application/pdf":
        # st.text("pdf: "+file.name)
        # base64_pdf = base64.b64encode(file.read()).decode("utf-8")
        # pdf_display = F'<iframe src="data:application/pdf;base64,\
        # {base64_pdf}" width="700" height="400" type="application/pdf"></iframe>'
        # st.markdown(pdf_display, unsafe_allow_html=True)
        call_llm = False
        question_dict = {}
        total_questions=0
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Bloom Taxonomy Levels")
            l1_questions = st.slider("Select the number of questions targeting Recall capability.", 0, 10, 0, 1)
            l2_questions = st.slider("Select the number of questions to evaluate Understanding of topic.", 0, 10, 0, 1)
            l3_questions = st.slider("Select the number of questions to evaluate Applicability of concepts.", 0, 10, 0, 1)
            l4_questions = st.slider("Select the number of questions to check Analysis of situtation using learned concepts.", 0, 10, 0, 1)

        with col2:
            st.subheader("Level of Description")
            detail_level = st.radio("Select the descriptiveness you want for the answers", 
                            ["Short", "Medium", "Detailed"],
                            captions = ["Direct responses", "Briefly explained answers", "Detailed responses but not exhausting."], index=1)
            
        # submit = st.button("Generate QnAs", type="primary")
            
        if (l1_questions + l2_questions + l3_questions + l4_questions) > 0 and (l1_questions + l2_questions + l3_questions + l4_questions) <= 10:
            question_dict[1] = l1_questions
            question_dict[2] = l2_questions
            question_dict[3] = l3_questions
            question_dict[4] = l4_questions
            total_questions = l1_questions + l2_questions + l3_questions + l4_questions
            call_llm = True
        else:
            print("Please select only total of 10 Questions")
            call_llm = False

        if call_llm and st.button("Learn By Questions and Answers", type="primary"):
            try:
                llm = llm.generator_llm(file)
                responses = llm.get_qna(total_questions, question_dict, detail_level)
                # with open(f'/mount/src/blank-app/data/{file.name.replace(".pdf", "").replace(".", "_").replace(" ", "_")}_{int(time.time())}.json', 'w') as datawriter:
                #     json.dump(json.loads(responses), datawriter)
                
                if type(responses) == "str" or type(responses)!="list":
                    try:
                        responses = json.loads(responses)
                        for i, res in enumerate(responses):
                            expander = st.expander("Q" + str(i+1) + ". " + res["question"])
                            expander.write("Answer: " + res["answer"])
                            expander.write("BTL: " + str(res["addressed_BTL"]))
                    except:
                        expected_resp = st.expander("Failed to load Json")
                        expected_resp.write(responses)
                    # print("\n\nFormatted Responses : ", responses)
                else:
                    json_resp = st.expander("Invalid Json Format Output")
                    json_resp.write(responses)
            except Exception as e:
                exception_ex = st.expander("Error Message")
                exception_ex.write(e)
        elif call_llm and st.button("Learn By Listening", type="primary"):
            llm = llm.generator_llm(file)
            responses = llm.get_audio()
            script_ex = st.expander("Audio Script")
            script_ex.write(responses)
            st.audio(f'{file.name.replace(".pdf", "").replace(".", "_").replace(" ", "_")}.mp3', format="audio/mpeg")

        elif call_llm==False:
            st.write("Please make sure to generate total of 10 queries only.")
            
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.write("Docx Not Supported right now.")
    else:
        st.write("Please upload pdf file.")
        #Implementation to be done.

    # Provide option to select Questions, BTL Levels and Content Length
