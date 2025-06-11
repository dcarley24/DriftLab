from flask import Flask, render_template, request, redirect, url_for
from openai_utils import generate_drift_chain, attempt_recovery, score_single_output, generate_reasoning
from prompt_templates import default_templates
from db import (
    insert_prompt, insert_output, insert_recovery,
    get_prompt_history, get_prompt_details
)
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

templates = default_templates.copy()

@app.route('/', methods=['GET', 'POST'])
def index():
    global templates

    outputs = []
    scores = []
    violations = []
    entropy_scores = []
    recovery_output = None
    recovery_score = None
    prompt = ""
    recovery_prompt = ""
    model = "gpt-3.5-turbo"
    show_recovery_prompt = False
    reasoning_text = None

    if request.method == 'POST' and 'prompt' in request.form:
        prompt = request.form['prompt']
        recovery_prompt = request.form.get('recovery_prompt', '')
        model = request.form.get('model', 'gpt-3.5-turbo')

        forbidden_terms = []
        if "but don't mention" in prompt.lower():
            split_prompt = prompt.lower().split("but don't mention")
            if len(split_prompt) > 1:
                forbidden_terms = [t.strip(" .") for t in split_prompt[1].split("and")]

        outputs, scores, violations, entropy_scores = generate_drift_chain(
            prompt, steps=3, model=model, forbidden_terms=forbidden_terms
        )

        prompt_id = insert_prompt(prompt)
        for i, out in enumerate(outputs):
            insert_output(prompt_id, i, out, scores[i], violations[i])

        if scores:
            reasoning_text = generate_reasoning(prompt, outputs, scores, entropy_scores, model=model)

        if not recovery_prompt and scores and scores[-1] < 0.6:
            show_recovery_prompt = True

        if recovery_prompt:
            recovery_output = attempt_recovery(outputs[-1], recovery_prompt, model=model)
            recovery_score = score_single_output(prompt, recovery_output)
            insert_recovery(prompt_id, recovery_prompt, recovery_output, recovery_score)

    return render_template('index.html',
                           prompt=prompt,
                           outputs=outputs,
                           scores=scores,
                           violations=violations,
                           entropy_scores=entropy_scores,
                           recovery_output=recovery_output,
                           recovery_score=recovery_score,
                           recovery_prompt=recovery_prompt,
                           templates=templates,
                           model=model,
                           show_recovery_prompt=show_recovery_prompt,
                           reasoning_text=reasoning_text)

@app.route('/add_template', methods=['POST'])
def add_template():
    global templates
    label = request.form['new_label']
    prompt = request.form['new_prompt']
    templates.append({"label": label, "prompt": prompt})
    return redirect(url_for('index'))

@app.route('/remove_template/<int:index>', methods=['POST'])
def remove_template(index):
    global templates
    if 0 <= index < len(templates):
        templates.pop(index)
    return redirect(url_for('index'))

@app.route('/history')
def history():
    rows = get_prompt_history()
    return render_template('history.html', rows=rows)

@app.route('/history/<int:prompt_id>')
def view_prompt(prompt_id):
    prompt, outputs, recoveries = get_prompt_details(prompt_id)
    return render_template('prompt_detail.html',
                           prompt_id=prompt_id,
                           prompt=prompt,
                           outputs=outputs,
                           recoveries=recoveries)


if __name__ == '__main__':
    print("Starting Drift Lab on http://0.0.0.0:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
