# 🎵 Musical Companion

### An AI-powered personalized music learning companion using RAG and LangGraph

Musical Companion is an AI-based learning application designed to help users learn and practice music.

It combines **Retrieval-Augmented Generation (RAG)**, **LangGraph**, **FAISS**, and **LLMs** to provide personalized explanations and practice guidance for:

- 🎸 Guitar
- 🎹 Piano
- 🎼 Music Theory

The application also provides structured exploration of chords and scales.

---

## ✨ Features

### 🎓 Learn

Ask questions about music theory, guitar, piano, chords, scales, and other musical concepts.

The system uses a RAG pipeline to retrieve relevant information from the project's music knowledge base before generating an answer.

---

### 🔎 Explore

Explore structured music data such as:

- Chords
- Scales
- Notes

The current structured music database contains examples such as:

- C major
- G major
- A minor
- E minor
- C major scale
- A natural minor scale
- C chromatic scale

---

### 🏋️ Practice

Ask Musical Companion to create a practice routine.

Practice suggestions are personalized according to:

- Instrument
- Skill level
- User request

Supported levels:

- Beginner
- Intermediate
- Advanced

---

### 🧠 Conversational Memory

Musical Companion keeps the conversation history during a session.

This allows follow-up questions to use previous context.

For example:

```text
User:
What is a major scale?

Assistant:
A major scale is...

User:
What about its interval pattern?

Assistant:
The major scale follows...