import streamlit as st
import json
import os
import re
import logging

# Setup basic logging to help debug in the terminal
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# DATA PRE-PROCESSING FUNCTION
# ==============================================================================
def preprocess_questions(questions_data):
    """
    Cleans the questions and options by removing leading numbers and letters.
    It also ensures the 'answer' field matches the cleaned option text.
    """
    processed_questions = []
    for q in questions_data:
        try:
            # Clean the question text
            cleaned_question = re.sub(r'^\d+\s*\.+\s*', '', q['question']).strip()
            
            # Clean the options text and find the original answer
            cleaned_options = []
            original_answer = ""
            
            # First, find the original full answer text
            if q['answer'].startswith(('a', 'b', 'c', 'd')):
                original_answer = re.sub(r'^[a-zA-Z][.)]\s*', '', q['answer']).strip()
            else:
                original_answer = q['answer']
                
            # Now, clean all options
            for opt in q['options']:
                cleaned_options.append(re.sub(r'^[a-zA-Z][.)]\s*', '', opt).strip())

            # Find the new, cleaned answer from the cleaned options list
            new_correct_answer = ""
            for opt in cleaned_options:
                # Check if the original answer is a substring of the cleaned option
                if original_answer in opt:
                    new_correct_answer = opt
                    break
            
            if new_correct_answer:
                processed_questions.append({
                    "question": cleaned_question,
                    "options": cleaned_options,
                    "answer": new_correct_answer
                })
            else:
                logging.warning(f"Could not match answer for question: {cleaned_question}")

        except Exception as e:
            logging.error(f"Failed to process question: {q}. Error: {e}")
            continue
            
    return processed_questions

# ==============================================================================
# STREAMLIT APPLICATION UI
# ==============================================================================
def main():
    st.set_page_config(page_title="Keedam Preload Quiz", page_icon="✈️", layout="centered")
    st.title("✈️ Keedam Preload Quiz App")

    # Initialize session state for all variables
    if 'state' not in st.session_state:
        st.session_state.state = 'initial'
        st.session_state.questions = []
        st.session_state.current_question = 0
        st.session_state.user_answers = {}

    # --- STATE 1: Initial File Selection Screen ---
    if st.session_state.state == 'initial':
        st.info("Select a quiz from the JSON files found in this folder.")
        
        try:
            # Find all .json files in the current directory
            json_files = [f for f in os.listdir('.') if f.endswith('.json')]
            
            if not json_files:
                st.error("No JSON quiz files found in this folder. Please add a quiz file.")
                return

            selected_file = st.selectbox("**1. Choose your quiz file:**", options=json_files)

            if st.button("Load Quiz"):
                with st.spinner(f"Loading '{selected_file}'..."):
                    with open(selected_file, 'r', encoding='utf-8') as f:
                        raw_questions = json.load(f)
                    
                    # Pre-process the questions to clean them up
                    st.session_state.questions = raw_questions
                
                if st.session_state.questions:
                    st.session_state.state = 'quiz_started'
                    st.rerun()
                else:
                    st.error("Could not load any valid questions from the selected file.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            logging.error(f"File loading/processing failed: {e}")
        return

    # --- STATE 2: Quiz is Finished ---
    if st.session_state.state == 'finished':
        # Calculate score ONLY at the end to ensure correctness
        score = sum(1 for i, q in enumerate(st.session_state.questions) if st.session_state.user_answers.get(i) == q['answer'])
        
        st.success(f"## 🎯 Quiz Complete!")
        st.write(f"### Your Final Score: {score} out of {len(st.session_state.questions)}")

        with st.expander("Review Your Answers"):
             for i, q in enumerate(st.session_state.questions):
                user_answer = st.session_state.user_answers.get(i, "Not Answered")
                correct_answer = q['answer']
                if user_answer == correct_answer:
                    st.markdown(f"**Q{i+1}: {q['question']}**\n\n✅ Your answer: `{user_answer}` (Correct)")
                else:
                    st.markdown(f"**Q{i+1}: {q['question']}**\n\n❌ Your answer: `{user_answer}`\n\nCorrect answer: `{correct_answer}`")
                st.markdown("---")
        
        if st.button("Take a New Quiz"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
        return

    # --- STATE 3 & 4: Answering and Feedback ---
    if st.session_state.state in ['quiz_started', 'show_feedback']:
        q_index = st.session_state.current_question
        q_data = st.session_state.questions[q_index]

        # --- NAVIGATION SECTION ---
        def jump_to_question():
            selected_q_text = st.session_state.question_jumper
            new_index = int(selected_q_text.split(" ")[1]) - 1
            st.session_state.current_question = new_index
            st.session_state.state = 'quiz_started'

        st.selectbox("Skip to question:", options=[f"Question {i+1}" for i in range(len(st.session_state.questions))],
            index=st.session_state.current_question, on_change=jump_to_question, key='question_jumper')
        st.markdown("---")

        st.subheader(f"Question {q_index + 1} of {len(st.session_state.questions)}")
        st.markdown(f"<p style='font-size: 20px; font-weight: 500;'>{q_data['question']}</p>", unsafe_allow_html=True)
        
        valid_options = [opt for opt in q_data["options"] if opt]
        
        if st.session_state.state == 'quiz_started':
            with st.form(key=f"form_{q_index}"):
                previous_answer = st.session_state.user_answers.get(q_index)
                previous_answer_index = valid_options.index(previous_answer) if previous_answer in valid_options else 0
                user_choice = st.radio("Choose your answer:", options=valid_options, key=f"radio_{q_index}", index=previous_answer_index)
                submitted = st.form_submit_button("Check Answer")
                if submitted:
                    st.session_state.user_answers[q_index] = user_choice
                    st.session_state.state = 'show_feedback'
                    st.rerun()
        
        elif st.session_state.state == 'show_feedback':
            last_answer = st.session_state.user_answers.get(q_index, "")
            try: default_index = valid_options.index(last_answer)
            except (ValueError, IndexError): default_index = 0
            
            st.radio("Your Answer:", options=valid_options, index=default_index, disabled=True)
            
            correct_answer = q_data['answer']
            if last_answer == correct_answer:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect! The correct answer was: **{correct_answer}**")
            

            is_last_question = (q_index + 1 == len(st.session_state.questions))
            button_text = "Finish Quiz" if is_last_question else "Next Question ->"
            if st.button(button_text,use_container_width=True):
                if not is_last_question:
                    st.session_state.current_question += 1
                    st.session_state.state = 'quiz_started'
                else:
                    st.session_state.state = 'finished'
                st.rerun()

if __name__ == "__main__":
    main()