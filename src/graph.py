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

    question = state["question"].lower()

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
        "bar",
        "fret",
        "frets",
        "fifth fret",
        "fourth fret",
        "third fret",
        "second fret",
        "first fret",
        "strumming",
        "hand position",
        "position on guitar"
    ]

    if any(word in question for word in instructional_words):

        return {
            "route": "rag"
        }


    for chord in CHORDS:

        if chord.lower() in question:

            return {
                "route": "music_data"
            }


    for scale in SCALES:

        if scale.lower() in question:

            return {
                "route": "music_data"
            }

    practice_words = [
        "practice",
        "exercise",
        "routine",
        "workout",
        "improve"
    ]

    if any(word in question for word in practice_words):

        return {
            "route": "practice"
        }

    return {
        "route": "rag"
    }

    # Check structured scale data
    for scale in SCALES:

        if scale.lower() in question:
            return {
                "route": "music_data"
            }


    practice_words = [
        "practice",
        "exercise",
        "routine",
        "workout",
        "improve"
    ]

    if any(word in question for word in practice_words):

        return {
            "route": "practice"
        }

    return {
        "route": "rag"
    }


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
"it", "its", "this", "that", or "the previous one".

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

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


def generate_music_data_answer(state: MusicState):

    question = state["question"].lower()

    # Search chords
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

Level guidelines:

- Beginner:
  Focus on fundamentals, simple exercises, slower practice,
  and clear step-by-step instructions.

- Intermediate:
  Include more challenging exercises, technique development,
  musical application, and moderate practice complexity.

- Advanced:
  Do not give a beginner routine.
  Include technically demanding exercises, deeper musical
  concepts, structured progression, and performance-oriented
  practice where appropriate.

Instrument guidelines:

- For Guitar, include guitar-specific techniques,
  fretboard work, chord changes, scales, picking,
  rhythm, or other relevant guitar skills when appropriate.

- For Piano, include piano-specific techniques,
  scales, arpeggios, chord voicings, coordination,
  rhythm, or other relevant piano skills when appropriate.

- For Music Theory, focus on theoretical analysis,
  ear training, harmony, composition, or related exercises.

Make the routine practical and specific.

Use numbered steps.
Put each numbered item on its own line.
Do not use HTML tags.
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }

    prompt = f"""
You are Musical Companion, an AI music practice assistant.

The user wants help with practice.

User question:
{state["question"]}

Conversation history:
{state["chat_history"]}

Give a simple and useful practice suggestion.

Keep it suitable for a beginner unless the question
clearly indicates another level.

Use numbered steps when appropriate.
Put each numbered item on its own line.
Do not use HTML tags.
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


def route_request(state: MusicState):

    if state["route"] == "music_data":

        return "music_data"

    if state["route"] == "practice":

        return "practice"

    return "rewrite"


graph_builder = StateGraph(MusicState)


# Nodes
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
