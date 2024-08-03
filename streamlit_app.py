import os
from dotenv import load_dotenv
import streamlit as st
import llm_util
import base64
import json
import time
import zipfile

load_dotenv()

st.header("Generate Question and Answers for Learning Unit", anchor=None, help=None, divider="blue")

file = st.file_uploader("Upload Unit document here", type=['pdf'], accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")

def download_audio():
    # ziph is zipfile handle
    print("In download audio")
    with zipfile.ZipFile('audio.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("./data/"):
            for file in files:
                if file.endswith('.mp3') or file.endswith('.wav'):
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join('./data', '..')))
        btn = st.download_button(
            label="Download Audio Files",
            data=zipf,
            file_name="audio.zip",
            mime="application/zip",
        )

def download_json():
    print("In download Json ")
    root="./data/"
    files = os.listdir(root)
    multiple_file = False
    if len(files) > 1:
        multiple_file = True
        
    if multiple_file:    
        with zipfile.ZipFile('./jsons.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filen in files:
                if filen.endswith('.json'):
                    zipf.write(root+filen, filen)
        with open("./jsons.zip", 'rb') as fp:
            btn = st.download_button(
                label="Download Json Files",
                data=fp,
                file_name="jsons.zip",
                mime="application/zip")
        os.remove("./jsons.zip")
    else:
        for jsonfiles in os.listdir("./data"):
            print(jsonfiles)
            with open(f"./data/{jsonfiles}", 'rb') as jfile:
                btn = st.download_button(
                    label="Download JSON File",
                    data=jfile,
                    file_name=jsonfiles,
                    mime="application/json",
                )
    for filen in files:
        os.remove(root+filen)

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
                llm = llm_util.generator_llm(file)
                responses = llm.get_qna(total_questions, question_dict, detail_level)
                # with open(f'/mount/src/blank-app/data/{file.name.replace(".pdf", "").replace(".", "_").replace(" ", "_")}_{int(time.time())}.json', 'w') as datawriter:
                #     json.dump(json.loads(responses), datawriter)
                
                if type(responses) == "str" or type(responses)!="list":
                    try:
                        llm_util.store_file(file, responses)
                        responses = json.loads(responses)
                        for i, res in enumerate(responses):
                            expander = st.expander("Q" + str(i+1) + ". " + res["question"])
                            expander.write("Answer: " + res["answer"])
                            expander.write("BTL: " + str(res["addressed_BTL"]))
                        download_json()
                    except Exception as e:
                        
                        expected_resp = st.expander("Failed to load Json")
                        expected_resp.write(e)
                        # expected_resp.write(responses + "\nError: " + e)
                    # print("\n\nFormatted Responses : ", responses)
                else:
                    json_resp = st.expander("Invalid Json Format Output")
                    json_resp.write(responses)
            except Exception as e:
                exception_ex = st.expander("Error Message")
                exception_ex.write(e)
        elif call_llm and st.button("Learn By Listening", type="primary"):
            llm = llm_util.generator_llm(file)
            responses = llm.get_audio()
            script_ex = st.expander("Audio Script")
            script_ex.write(responses)
            st.audio(f'{file.name.replace(".pdf", "").replace(".", "_").replace(" ", "_")}.mp3', format="audio/mpeg")
            # `llm_util.download_audio()` is a function that is likely used to download the audio file
            # generated by the learning model (LLM) utility. This function is expected to handle the
            # downloading process of the audio file, making it accessible to the user for offline
            # listening or storage.
            # llm_util.download_audio()
            download_audio()

        elif call_llm==False:
            st.write("Please make sure to generate total of 10 queries only.")
            
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        st.write("Docx Not Supported right now.")
    else:
        st.write("Please upload pdf file.")
        #Implementation to be done.

    # Provide option to select Questions, BTL Levels and Content Length
