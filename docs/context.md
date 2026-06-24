# Project Context: AI-Powered Restaurant Recommendation System

## Overview

This project is an **AI-powered restaurant recommendation service** inspired by Zomato. The system intelligently suggests restaurants based on user preferences by combining structured data with a **Large Language Model (LLM)**.

---

## Objective

Design and implement an application that:

1. Takes user preferences (such as location, budget, cuisine, and ratings)
2. Uses a real-world dataset of restaurants
3. Leverages an LLM to generate personalized, human-like recommendations
4. Displays clear and useful results to the user

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face  
  **Dataset URL:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - (and other applicable fields from the dataset)

### 2. User Input

Collect user preferences:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional preferences** | family-friendly, quick service |

### 3. Integration Layer

- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason and rank options

### 4. Recommendation Engine

Use the LLM to:

- Rank restaurants
- Provide explanations (why each recommendation fits)
- Optionally summarize choices

### 5. Output Display

Present top recommendations in a user-friendly format:

- Restaurant Name
- Cuisine
- Rating
- Estimated Cost
- AI-generated explanation

---

## Key Technical Components

| Component | Responsibility |
|-----------|----------------|
| **Data pipeline** | Load Hugging Face dataset, preprocess, extract fields |
| **Preference collection** | Capture location, budget, cuisine, rating, and free-form preferences |
| **Filtering layer** | Narrow restaurant list before LLM processing |
| **LLM integration** | Prompt design, ranking, explanation generation |
| **UI / output** | Display ranked recommendations with structured metadata and AI explanations |

---

## Data Source

- **Platform:** Hugging Face
- **Dataset:** `ManikaSaini/zomato-restaurant-recommendation`
- **Link:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation

---

## Success Criteria

The application is successful when it:

- Accepts meaningful user preferences
- Filters real restaurant data against those preferences
- Uses an LLM to produce ranked, explained recommendations
- Presents results clearly with name, cuisine, rating, cost, and rationale
