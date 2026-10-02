import streamlit as st

from src.graph import graph
from data.music_data import CHORDS, SCALES


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []



st.set_page_config(
    page_title="Musical Companion",
    page_icon="🎵",
    layout="wide"
)



st.title("🎵 Musical Companion")

st.caption(
    "An AI-powered companion for learning music theory, "
    "guitar, and piano."
)



st.sidebar.title("🎼 Learning Profile")

instrument = st.sidebar.selectbox(
    "Instrument",
    [
        "Guitar",
        "Piano",
        "Music Theory"
    ]
)

level = st.sidebar.selectbox(
    "Level",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)

mode = st.sidebar.radio(
    "Learning Mode",
    [
        "🎓 Learn",
        "🔎 Explore",
        "🏋️ Practice"
    ]
)

st.sidebar.divider()

st.sidebar.write(
    f"**Instrument:** {instrument}"
)

st.sidebar.write(
    f"**Level:** {level}"
)


if mode == "🎓 Learn":

    st.header("🎓 Learn")

    st.write(
        "Ask questions and learn music concepts "
        "with explanations suited to your level."
    )

  
    for message in st.session_state.chat_history:

        if message.startswith("User: "):

            st.chat_message("user").write(
                message.replace("User: ", "", 1)
            )

        elif message.startswith("Assistant: "):

            st.chat_message("assistant").markdown(
                message.replace("Assistant: ", "", 1)
            )

    question = st.chat_input(
        "What would you like to learn?"
    )

    if question:

       
        history_text = "\n".join(
            st.session_state.chat_history
        )

        result = graph.invoke({
    "question": question,
    "context": "",
    "answer": "",
    "route": "",
    "chat_history": history_text,
    "search_query": "",
    "instrument": instrument,
    "level": level
})
    
        st.chat_message("user").write(question)

     
        answer = result["answer"]

   
        answer = answer.replace("<br>", "\n")
        answer = answer.replace("<br/>", "\n")
        answer = answer.replace("<br />", "\n")

       
        answer = answer.replace(" 1. ", "\n1. ")
        answer = answer.replace(" 2. ", "\n2. ")
        answer = answer.replace(" 3. ", "\n3. ")
        answer = answer.replace(" 4. ", "\n4. ")
        answer = answer.replace(" 5. ", "\n5. ")

    
        st.chat_message("assistant").markdown(answer)

   
        st.session_state.chat_history.append(
            f"User: {question}"
        )

        st.session_state.chat_history.append(
            f"Assistant: {answer}"
        )



elif mode == "🔎 Explore":

    st.header("🔎 Explore")

    st.write(
        "Explore chords and scales from the "
        "Musical Companion music database."
    )

    explore_type = st.selectbox(
        "What would you like to explore?",
        [
            "Chords",
            "Scales"
        ]
    )

    if explore_type == "Chords":

        chord_name = st.selectbox(
            "Choose a chord",
            list(CHORDS.keys())
        )

        chord = CHORDS[chord_name]

        st.subheader(chord_name)

        st.write(
            f"**Type:** {chord['type']}"
        )

        st.write(
            "**Notes:** " + " - ".join(chord["notes"])
        )

    else:

        scale_name = st.selectbox(
            "Choose a scale",
            list(SCALES.keys())
        )

        scale = SCALES[scale_name]

        st.subheader(scale_name)

        st.write(
            "**Notes:** " + " - ".join(scale)
        )



elif mode == "🏋️ Practice":

    st.header("🏋️ Practice")

    st.write(
        "Build practice routines and improve your "
        "musical skills."
    )

    question = st.chat_input(
        "What would you like to practice?"
    )

    if question:

        history_text = "\n".join(
            st.session_state.chat_history
        )

        result = graph.invoke({
    "question": question,
    "context": "",
    "answer": "",
    "route": "",
    "chat_history": history_text,
    "search_query": "",
    "instrument": instrument,
    "level": level
})

        st.chat_message("user").write(question)

        answer = result["answer"]

  
        answer = answer.replace("<br>", "\n")
        answer = answer.replace("<br/>", "\n")
        answer = answer.replace("<br />", "\n")

       
        answer = answer.replace(" 1. ", "\n1. ")
        answer = answer.replace(" 2. ", "\n2. ")
        answer = answer.replace(" 3. ", "\n3. ")
        answer = answer.replace(" 4. ", "\n4. ")
        answer = answer.replace(" 5. ", "\n5. ")

        st.chat_message("assistant").markdown(answer)

        st.session_state.chat_history.append(
            f"User: {question}"
        )

        st.session_state.chat_history.append(
            f"Assistant: {answer}"
        )
