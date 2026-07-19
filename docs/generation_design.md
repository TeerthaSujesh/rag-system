# Generation Module Design

## Purpose

The Generation Module is responsible for generating the final answer in the Retrieval-Augmented Generation (RAG) pipeline. It receives the user's question along with the relevant document chunks retrieved by the retrieval module. Using Llama 3.2 3B, it generates an accurate answer based only on the provided context.

The module is designed to minimize hallucinations, preserve the original wording of the document whenever possible, and produce a clean, readable response.

---

# Inputs

The module receives two inputs:

1. User Question
   - The question entered by the user.

2. Retrieved Context
   - The top relevant chunks returned by the Retrieval Module.
   - These chunks provide the information required to answer the question.

Example:

Question:
What is Python?

Context:
Python is a high-level programming language.
Python supports object-oriented programming.
Python has simple syntax.

---

# Outputs

The module returns:

- A final natural language answer generated using the provided context.
- (Optional) Source information such as page number or document section.

Example:

Answer:
Python is a high-level programming language.

Source:
Page 4

---

# Responsibilities of Each File

## config.py

Stores configuration variables used throughout the generation module.

Examples:
- Model name
- Temperature
- Top-p
- Maximum tokens

Keeping configuration separate makes it easy to modify settings without changing the program logic.

---

## model.py

Responsible for loading and communicating with the language model (Llama 3.2 3B).

Responsibilities:
- Load the model
- Send prompts to the model
- Receive generated responses

This isolates model-specific code from the rest of the application.

---

## prompts.py

Contains all prompt templates used for answer generation.

Different prompt styles can be stored here, such as:

- Strict prompt
- Normal prompt
- Quote-based prompt

This allows easy experimentation without modifying the generation logic.

---

## generator.py

Acts as the main controller of the generation module.

Responsibilities:

- Receive the question and retrieved context
- Select the appropriate prompt
- Send the prompt to the model
- Receive the generated response
- Pass the response to the formatter
- Return the final answer

This file coordinates all components of the module.

---

## formatter.py

Responsible for formatting the generated response.

Examples:

- Add headings
- Display source information
- Format multi-line answers
- Improve readability

---

# Overall Workflow

```
User Question
        +
Retrieved Context
        |
        v
Prompt Engineering
        |
        v
Llama 3.2 3B
        |
        v
Generated Response
        |
        v
Response Formatting
        |
        v
Final Answer
```

---

# Design Principles

The Generation Module follows the principle of separation of concerns.

Each file has a single responsibility:

- Configuration is stored separately.
- Prompt templates are isolated.
- Model interaction is independent.
- Formatting is handled separately.
- Generation logic remains clean and modular.

This design makes the module easier to maintain, test, and extend in the future.

---

# Future Improvements

Possible future enhancements include:

- Prompt optimization
- Better response formatting
- Automatic source citation
- Multiple prompt selection strategies
- Support for additional language models
- Evaluation metrics such as Exact Match and Hallucination Rate
- Whether hierarchical chunking is worth the added complexity given time constraints.
- Sliding window chunking is not implemented as a separate strategy: it's the same algorithm as fixed-size chunking with overlap > 0 (see FixedSizeChunker's docstring). Comparison results for "fixed-size" in task 1 cover both cases by varying overlap.