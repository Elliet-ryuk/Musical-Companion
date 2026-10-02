from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.rag_pipeline import retriever, llm
from src.prompts import MUSIC_RAG_PROMPT
from data.music_data import CHORDS, SCALES


class MusicState(TypedDict):
    question: str
    context: str
    answer: str
    route: str
    chat_history: str
    search_query: str
    instrument: str
    level: str

def classify_request(state: MusicState):

    question = state["question"].lower().strip()

    explanation_words = [
        "what is",
        "what are",
        "what's",
        "why",
        "explain",
        "difference",
        "different",
        "compare",
        "comparison",
        "meaning",
        "understand",
        "tell me about",
        "describe",
        "how does",
        "how do",
    ]


    instructional_words = [
        "how to play",
        "how do i play",
        "how can i play",
        "fingering",
        "finger position",
        "finger positions",
        "chord shape",
        "shape",
        "barre",
        "bar chord",
        "fret",
        "frets",
        "fifth fret",
        "fourth fret",
        "third fret",
        "second fret",
        "first fret",
        "strumming",
        "hand position",
        "position on guitar",
        "how should i play",
    ]

    # Explanation questions → RAG
    if any(word in question for word in explanation_words):
        return {"route": "rag"}

    # Instructional questions → RAG
    if any(word in question for word in instructional_words):
        return {"route": "rag"}


    practice_words = [
        "practice",
        "exercise",
        "routine",
        "workout",
        "improve",
        "training",
        "train",
    ]

    if any(word in question for word in practice_words):
        return {"route": "practice"}


    for chord in CHORDS:
        if chord.lower() in question:
            return {"route": "music_data"}

    for scale in SCALES:
        if scale.lower() in question:
            return {"route": "music_data"}


    return {"route": "rag"}


def route_request(state: MusicState):

    if state["route"] == "music_data":
        return "music_data"

    if state["route"] == "practice":
        return "practice"

    return "rewrite"



def rewrite_search_query(state: MusicState):

    question = state["question"]
    chat_history = state["chat_history"]


    if not chat_history.strip():

        return {
            "search_query": question
        }

    prompt = f"""
You are helping an AI music-learning system retrieve
information from a music knowledge base.

Rewrite the user's latest question into a clear,
self-contained search query.

Use the conversation history to understand words such as:

- it
- its
- this
- that
- the previous one
- the above chord
- the above scale

Do not answer the question.

Return ONLY the rewritten search query.

Conversation history:
{chat_history}

Latest user question:
{question}

Rewritten search query:
"""

    response = llm.invoke(prompt)

    search_query = response.content.strip()

    return {
        "search_query": search_query
    }


def retrieve_knowledge(state: MusicState):

    search_query = state["search_query"]

    results = retriever.invoke(search_query)

    context = "\n\n".join(
        result.page_content
        for result in results
    )

    return {
        "context": context
    }




def generate_rag_answer(state: MusicState):

    prompt = MUSIC_RAG_PROMPT.format(
        context=state["context"],
        chat_history=state["chat_history"],
        question=state["question"],
        instrument=state["instrument"],
        level=state["level"]
    )

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


def generate_music_data_answer(state: MusicState):

    question = state["question"].lower()



    for chord_name, chord_data in CHORDS.items():

        if chord_name.lower() in question:

            answer = (
                f"**{chord_name}**\n\n"
                f"Type: {chord_data['type']}\n\n"
                f"Notes: {' - '.join(chord_data['notes'])}"
            )

            return {
                "answer": answer
            }


    for scale_name, notes in SCALES.items():

        if scale_name.lower() in question:

            answer = (
                f"**{scale_name}**\n\n"
                f"Notes: {' - '.join(notes)}"
            )

            return {
                "answer": answer
            }

    return {
        "answer": "I couldn't find that item in the music database."
    }



def generate_practice_answer(state: MusicState):

    prompt = f"""
You are Musical Companion, an AI music practice assistant.

The user wants a practice routine.

Learner profile:
Instrument: {state["instrument"]}
Level: {state["level"]}

Conversation history:
{state["chat_history"]}

User question:
{state["question"]}

Create a practice routine that matches the learner's
instrument and skill level.

LEVEL GUIDELINES:

Beginner:
- Focus on fundamentals.
- Use simple exercises.
- Use slower practice.
- Give clear step-by-step instructions.
- Avoid unnecessary technical complexity.

Intermediate:
- Include more challenging exercises.
- Include technique development.
- Include musical application.
- Use moderate practice complexity.

Advanced:
- Do not give a beginner routine.
- Include technically demanding exercises.
- Include deeper musical concepts.
- Include structured progression.
- Include performance-oriented practice where appropriate.

INSTRUMENT GUIDELINES:

Guitar:
- Chord changes
- Fretboard work
- Scales
- Picking
- Rhythm
- Strumming
- Technique

Piano:
- Scales
- Arpeggios
- Chord voicings
- Hand coordination
- Rhythm
- Technique

Music Theory:
- Ear training
- Harmony
- Chord analysis
- Scale analysis
- Composition
- Musical analysis

Make the routine practical and specific.

Use numbered steps.

Put each numbered item on its own line.

Do not use HTML tags.

Do not use <br>.

"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


graph_builder = StateGraph(MusicState)


# Add nodes
graph_builder.add_node(
    "classify",
    classify_request
)

graph_builder.add_node(
    "rewrite",
    rewrite_search_query
)

graph_builder.add_node(
    "retrieve",
    retrieve_knowledge
)

graph_builder.add_node(
    "rag_answer",
    generate_rag_answer
)

graph_builder.add_node(
    "music_data",
    generate_music_data_answer
)

graph_builder.add_node(
    "practice",
    generate_practice_answer
)



graph_builder.add_edge(
    START,
    "classify"
)

graph_builder.add_conditional_edges(
    "classify",
    route_request,
    {
        "rewrite": "rewrite",
        "music_data": "music_data",
        "practice": "practice"
    }
)

graph_builder.add_edge(
    "rewrite",
    "retrieve"
)

graph_builder.add_edge(
    "retrieve",
    "rag_answer"
)

graph_builder.add_edge(
    "rag_answer",
    END
)


graph_builder.add_edge(
    "music_data",
    END
)


graph_builder.add_edge(
    "practice",
    END
)



graph = graph_builder.compile()