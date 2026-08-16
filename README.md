# 🧠 DSA Coach

An AI-powered Dynamic Programming learning platform that combines
Retrieval-Augmented Generation (RAG), Google Gemini, Pinecone, and
interactive learning tools to help students learn and practice
Dynamic Programming.

---

## 🚀 Overview

DSA Coach is an interactive learning assistant designed specifically
for Dynamic Programming.

Instead of providing generic AI answers, the application retrieves
relevant information from curated Dynamic Programming study material
using a RAG pipeline and uses that context to generate grounded,
topic-aware responses.

The platform also provides a structured DP learning roadmap, learning
videos, image-based questions, voice-based questions, and an AI-powered
practice system.

---

## ✨ Features

### 🤖 AI DP Coach

The Coach provides four learning modes:

- **Learn** — Understand DP concepts with detailed explanations.
- **Hint** — Get guidance without immediately receiving the solution.
- **Solution** — Get a complete explanation and solution approach.
- **Practice** — Generate and evaluate Dynamic Programming problems.

The Coach also considers:

- Current DP topic
- Previous conversation history
- Retrieved study material

---

### 📚 RAG-Based Learning

DSA Coach uses Retrieval-Augmented Generation to provide answers based
on curated Dynamic Programming study material.

The pipeline is:

```text
Study Material
      ↓
Document Chunking
      ↓
Sentence Transformer Embeddings
      ↓
Pinecone Vector Database
      ↓
Semantic Retrieval
      ↓
Relevant Context
      ↓
Google Gemini
      ↓
AI Coach Response
