// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const evaluateButton = document.getElementById('evaluateButton');
    if (evaluateButton) {
        evaluateButton.addEventListener('click', handleEvaluationSubmit);
    }
});

async function handleEvaluationSubmit(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];
    if (!file) {
        showError('Please select a CSV file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading('Evaluating translations...');
        const response = await fetch('/api/evaluate-translations', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to evaluate translations');
        }
        
        const result = await response.json();
        displayEvaluationResults(result);
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function displayEvaluationResults(data) {
    const resultsDiv = document.getElementById('evaluation-results');
    
    // Display summary
    const summaryHtml = `
        <div class="summary-card">
            <h3>Summary</h3>
            <div class="metrics-grid">

                <div class="metric">
                    <label>Average Accuracy</label>
                    <span>${data.summary.avg_accuracy.toFixed(2)}/10</span>
                </div>
                <div class="metric">
                    <label>Average Fluency</label>
                    <span>${data.summary.avg_fluency.toFixed(2)}/10</span>
                </div>
            </div>
        </div>
    `;
    
    // Display individual results
    const detailsHtml = data.results.map((result, index) => `
        <div class="result-card">
            <h4>Translation #${index + 1}</h4>
            <div class="translation-text">
                <p><strong>Source:</strong> ${escapeHtml(result.source_text)}</p>
                <p><strong>Reference:</strong> ${escapeHtml(result.reference_translation)}</p>
                <p><strong>New Translation:</strong> ${escapeHtml(result.new_translation)}</p>
            </div>
            <div class="metrics-grid">

                <div class="metric">
                    <label>Accuracy Score</label>
                    <span>${result.llm_evaluation.accuracy_score}/10</span>
                </div>
                <div class="metric">
                    <label>Fluency Score</label>
                    <span>${result.llm_evaluation.fluency_score}/10</span>
                </div>
            </div>
            <div class="comments">
                <strong>Comments:</strong>
                <p>${result.llm_evaluation.comments}</p>
            </div>
        </div>
    `).join('');
    
    resultsDiv.innerHTML = summaryHtml + detailsHtml;
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
