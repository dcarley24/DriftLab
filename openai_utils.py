import openai
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.stats import entropy

client = openai.OpenAI()

def calculate_information_density(text):
    if not text.strip():
        return 0.0
    probs = [text.count(c) / len(text) for c in set(text)]
    text_entropy = entropy(probs, base=2)
    max_entropy = np.log2(len(set(text))) if len(set(text)) > 1 else 1
    normalized_entropy = text_entropy / max_entropy
    return round(normalized_entropy, 3)

def generate_drift_chain(base_prompt, steps=3, model="gpt-3.5-turbo", forbidden_terms=[]):
    outputs = []
    violations = []
    entropy_scores = []
    current_input = base_prompt

    for i in range(steps):
        # Using context collapse simulation
        if i > 0:
            current_input = outputs[-1]

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Respond clearly and completely, adhering to the original task."},
                {"role": "user", "content": current_input}
            ],
            temperature=0.7
        )
        output = response.choices[0].message.content.strip()
        outputs.append(output)

        violation = check_constraints(output, forbidden_terms)
        violations.append(violation)

        entropy_scores.append(calculate_information_density(output))

    drift_scores = compute_drift_scores(base_prompt, outputs, violations)

    return outputs, drift_scores, violations, entropy_scores

def compute_drift_scores(prompt, outputs, violations):
    vectorizer = TfidfVectorizer().fit([prompt] + outputs)
    prompt_vec = vectorizer.transform([prompt])
    scores = []
    VIOLATION_PENALTY = 0.5

    for i, output in enumerate(outputs):
        output_vec = vectorizer.transform([output])
        score = cosine_similarity(prompt_vec, output_vec)[0][0]
        if violations[i]:
            score -= VIOLATION_PENALTY
        final_score = max(0.0, round(score, 3))
        scores.append(final_score)
    return scores

def generate_reasoning(original_prompt, outputs, drift_scores, entropy_scores, model="gpt-3.5-turbo"):
    """
    Analyzes both drift and entropy scores to provide a vibrant, concise summary.
    """
    final_drift_score = drift_scores[-1]

    entropy_trend = "stable"
    if len(entropy_scores) > 1:
        if entropy_scores[-1] < entropy_scores[0] - 0.05:
            entropy_trend = "decreased, suggesting a collapse in creativity or simplification of language"
        elif entropy_scores[-1] > entropy_scores[0] + 0.05:
            entropy_trend = "increased, suggesting a shift to more complex or jargon-filled language"

    # MODIFICATION: Made the prompt much more explicit about the two-paragraph structure.
    reasoning_prompt = f"""
You are an expert AI analyst. Your task is to explain the results of an AI simulation.
Your response MUST be two separate paragraphs, separated by '|||'.

**Paragraph 1:** Analyze the Prompt Fidelity Score of {final_drift_score:.3f}. A score below 0.6 indicates a significant drift. Explain what this means in terms of the AI failing its original mission or wandering off-topic.

**Paragraph 2:** Analyze the Language Complexity Trend, which was '{entropy_trend}'. Explain what this trend suggests about the creativity, repetitiveness, or structure of the AI's language as the simulation progressed.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert AI analyst providing concise, vibrant summaries in two paragraphs."},
            {"role": "user", "content": reasoning_prompt}
        ],
        temperature=0.5,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

def score_single_output(prompt, output):
    vectorizer = TfidfVectorizer().fit([prompt, output])
    vec_prompt = vectorizer.transform([prompt])
    vec_output = vectorizer.transform([output])
    score = cosine_similarity(vec_prompt, vec_output)[0][0]
    return round(score, 3)

def check_constraints(output, forbidden_terms):
    if not forbidden_terms:
        return False
    lowered_output = output.lower()
    return any(term.lower() in lowered_output for term in forbidden_terms)

def attempt_recovery(last_output, nudge_prompt, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are helping correct or realign previous AI output."},
            {"role": "user", "content": last_output},
            {"role": "user", "content": nudge_prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()
