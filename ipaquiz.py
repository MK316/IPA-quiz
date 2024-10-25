import pandas as pd
import random
import streamlit as st

# Load the CSV data synchronously for simplicity in Streamlit
def load_data():
    url = "IPA.csv"  # Make sure this is the correct path or URL for your file
    try:
        data = pd.read_csv(url, encoding='utf-8')
        if 'IPA' not in data.columns:
            raise ValueError("The required 'IPA' column is missing in the data.")
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# Properties to ask about for each IPA symbol
properties = ['Voicing', 'Place', 'Centrality', 'Oro-nasal', 'Manner']

# Generate a new question
def generate_question(used_ipa_symbols):
    if df.empty or 'IPA' not in df.columns:
        raise ValueError("IPA data is not loaded properly or missing.")
    
    # Loop until we get a valid IPA symbol that hasn't been used yet
    while True:
        current_ipa = df.sample(1).iloc[0]
        if not pd.isnull(current_ipa['IPA']) and current_ipa['IPA'] not in used_ipa_symbols:
            available_properties = [prop for prop in properties if not pd.isnull(current_ipa[prop])]
            if available_properties:
                break

    used_ipa_symbols.append(current_ipa['IPA'])
    property_name = random.choice(available_properties)
    question = f"IPA Symbol: {current_ipa['IPA']}\nWhat is the {property_name.lower()} of this IPA symbol?"
    answer = str(current_ipa[property_name]).strip().lower()  # Ensure the answer is stripped and lowercased
    return question, answer, used_ipa_symbols

# Check the answer and update the score and trials
def quiz_function(user_answer, correct_answer, score, trials):
    if user_answer.strip().lower() == correct_answer:  # Case-insensitive and stripping spaces
        score += 1
        result = f"Correct! The answer was '{correct_answer}'."
    else:
        result = f"Wrong! The correct answer was '{correct_answer}'."
    trials += 1
    return result, score, trials

# Initialize session state if it doesn't exist
if 'score' not in st.session_state:
    st.session_state.score = 0
    st.session_state.trials = 0
    st.session_state.used_ipa_symbols = []
    st.session_state.current_answer = ""
    st.session_state.name = ""
    st.session_state.question = ""
    st.session_state.quiz_started = False
    st.session_state.show_next = False  # New flag to handle showing next question

# Get user name
st.title("IPA Quiz")
name = st.text_input("Enter your name", st.session_state.name)
if name:
    st.session_state.name = name

# Start quiz button
if st.button("Start Quiz") and not st.session_state.quiz_started:
    if name:
        try:
            question, answer, used_ipa_symbols = generate_question(st.session_state.used_ipa_symbols)
            st.session_state.current_answer = answer
            st.session_state.used_ipa_symbols = used_ipa_symbols
            st.session_state.question = question
            st.session_state.quiz_started = True
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please enter your name to start the quiz.")

# Display the question if the quiz has started
if st.session_state.quiz_started:
    st.subheader(st.session_state.question)

    # User input for the answer
    user_answer = st.text_input("Your Answer", key="user_answer_input")

    # Submit button
    if st.button("Submit"):
        if user_answer:
            # Check the answer
            result, st.session_state.score, st.session_state.trials = quiz_function(
                user_answer, st.session_state.current_answer, st.session_state.score, st.session_state.trials
            )
            st.success(result)
            st.session_state.show_next = True  # Allow showing the next question
            
        else:
            st.error("Please enter an answer before submitting.")

    # Show next question button only if a question was just answered
    if st.session_state.show_next:
        if st.button("Show Next Symbol"):
            try:
                question, answer, used_ipa_symbols = generate_question(st.session_state.used_ipa_symbols)
                st.session_state.current_answer = answer
                st.session_state.used_ipa_symbols = used_ipa_symbols
                st.session_state.question = question
                st.session_state.show_next = False  # Reset the flag
                # Clear the user input field for the next question by rerunning the app state
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Quit button
    if st.button("Quit"):
        st.success(f"Quiz ended. Well done, {st.session_state.name}! Your total score: {st.session_state.score}/{st.session_state.trials} points.")
        # Reset the session state
        st.session_state.score = 0
        st.session_state.trials = 0
        st.session_state.used_ipa_symbols = []
        st.session_state.current_answer = ""
        st.session_state.name = ""
        st.session_state.question = ""
        st.session_state.quiz_started = False
        st.session_state.show_next = False
