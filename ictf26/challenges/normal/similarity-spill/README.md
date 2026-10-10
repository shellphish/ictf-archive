# Similarity Spill

**Category:** ML | **Points:** 500

## Description

A semantic-search system leaked a query embedding. The flag is hidden somewhere in the snippet collection. Can you recover it?

## Files

- `src/INSTRUCTIONS.txt` — task instructions
- `src/query.txt` — leaked query embedding vector
- `src/snippets.csv` — snippets with their embedding vectors

## Challenge Structure

Static challenge — no interactive service. Provides a leaked query embedding vector and a CSV of text snippets each paired with an 8-dimensional embedding vector. The challenge requires offline vector similarity analysis to identify the most relevant snippet.
