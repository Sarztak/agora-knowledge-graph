# Building a Legal Knowledge Graph for AI Policy Documents

## Overview

This project builds a **queryable legal knowledge graph (KG)** from U.S. AI governance and regulatory documents. The goal is to move beyond keyword search and shallow retrieval by explicitly modeling **institutional actors, obligations, authorities, and regulatory actions** expressed in legal text.

The system focuses on **who is responsible for what**, **under which legal instruments**, and **in relation to which risks, technologies, and domains**. The resulting graph supports structural analysis of AI regulation and exposes both the power and the limitations of rule-based legal information extraction at scale.

## Key Contributions

* **Structured obligation extraction**
  Identifies legally meaningful relationships such as mandates, reporting requirements, and regulatory authority between actors and targets.

* **Risk and technology mapping**
  Links legal sources to policy concerns (e.g. transparency, safety, national security) and application domains (healthcare, defense, data systems).

* **Normalized legal action ontology**
  Collapses noisy verb phrases into a small, semantically meaningful set of legal action types (e.g. OBLIGATE, REGULATE, REPORT).

* **Graph-based representation**
  Implements a directed legal knowledge graph in **Neo4j**, enabling exploration of oversight structures and regulatory concentration.

* **Empirical comparison with RAG**
  Evaluates graph-based retrieval (Graph RAG) against conventional text-based RAG to expose trade-offs between structure and semantic fidelity.

## Dataset

### AGORA — AI Governance and Regulatory Archive

* **Source**: Zenodo (2025), provided by the Emerging Technology Observatory
* **Content**:
  U.S. AI-related laws, bills, executive orders, regulations, and government actions
* **Includes**:
  Full text, metadata, long summaries, thematic tags

**Dataset statistics**

* Documents: 951
* Avg. words per long summary: 119
* Avg. tokens per sentence: 23

### Example Document

**California Assembly Bill 3030 (2024)**
Regulates the use of generative AI in healthcare communications by mandating disclosure requirements, defining key AI terms, and establishing enforcement mechanisms. Tagged for transparency risk and medical applications.

## Regulatory Landscape Analysis

* **Defense and national security dominate** AI regulation volume
* Healthcare and law enforcement are also heavily regulated
* Thematic clustering (TF-IDF + K-Means) reveals 7 major regulatory clusters:

  * Defense
  * National Security
  * Content / Media
  * Research & Development
  * Data / Automated Decision-Making
  * Safety
  * Task Forces

Clusters overlap due to shared legal language, but differ in thematic emphasis.

## System Architecture

### Multi-Step Knowledge Graph Pipeline

1. **Text preprocessing**
2. **Named Entity Recognition (SpaCy + domain rules)**
3. **Dependency parsing**
4. **Subject–Verb–Object triple extraction**
5. **Verb normalization into legal action ontology**
6. **Graph construction in Neo4j**
7. **Filtering to retain semantically meaningful relations**

### Generic Parsing Fails

Legal language routinely breaks standard NLP assumptions:

* Legal nouns double as verbs (“order”, “report”, “bill”)
* Obligations span multiple clauses
* Meaning depends on modality (“shall”, “may”, “is authorized to”)

Result: structurally valid triples that are **semantically shallow or misleading**.

To mitigate this, the graph retains only **collapsed legal action categories** rather than raw verbs.

## Knowledge Graph Design

### Nodes

* Unified entity type (actors, institutions, legal sources, targets)
* Attributes include:

  * name
  * category
  * document ID

### Relationships

* Directed: **actor → target**
* Normalized action types:

  * OBLIGATE
  * REGULATE
  * AUTHORIZE
  * REPORT
  * DEVELOP
  * IMPLEMENT
  * COORDINATE
  * RESTRICT
  * SUPPORT
  * EVALUATE
  * USE
  * OTHER

### Graph Statistics

* Nodes: 887
* Relationships: 653

Dense central clusters represent repeated legal responsibilities; sparse peripheries represent isolated mentions.

## Findings

* **Congress** is the dominant source of obligations
* **Department of Defense** is the most heavily obligated executive actor
* States (e.g. General Assemblies, Governors) play a significant regulatory role
* AI regulation is widespread, but **the graph cannot capture regulatory content**, only the existence of regulatory relationships

The KG answers *who regulates whom*, not *how* or *under what conditions*.

## Query and Retrieval System

### Query Flow

1. User query → SpaCy NER
2. Semantic matching to KG nodes
3. Neighborhood triple extraction
4. Cosine similarity scoring
5. LLM-generated response

### RAG Comparison

**Graph RAG**

* Preserves structure
* Low semantic recall
* Triples often insufficient for meaningful answers

**Text RAG**

* High relevance and recall
* Scales well
* Loses institutional structure

This exposes a core trade-off: **structure vs. semantic richness**.

## Design Assumptions and Limitations

### Assumptions

* Triples capture enough signal to be useful
* Verb normalization is viable
* Scale matters more than semantic depth at first pass

### Observed Limitations

* Loss of modality and conditional logic
* Multi-word legal predicates break extraction
* High semantic noise despite clean structure
* Entity accuracy does not guarantee meaningful relationships

## Core Insight

Legal knowledge graphs are **not about English sentences**.
They are about **institutional actions, authority, obligation, and constraint**.

* Entities alone carry no meaning
* Relationships define meaning
* Poor relationships collapse semantic value
* Extraction quality can only be judged **after graph construction and querying**

Triples are a weak approximation of meaning. The usefulness of a legal KG depends entirely on how well relationships abstract legal intent.

## Future Work

* LLM-based and agentic extraction (e.g. LangGraph)
* Hybrid rule-based + LLM pipelines
* Gold-standard annotated dataset for evaluation
* Deeper integration of KG with retrieval systems for robust legal QA

## Tech Stack

* Python
* SpaCy
* Neo4j
* TF-IDF + K-Means
* Cosine similarity
* RAG

---