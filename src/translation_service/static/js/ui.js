class UI {
    static showLoading(message = 'Processing... Please wait...') {
        const loading = document.getElementById('loading');
        loading.textContent = message;
        loading.style.display = 'block';
    }

    static hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    static showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const results = document.querySelector('.results');
        results.insertBefore(errorDiv, results.firstChild);
        
        setTimeout(() => errorDiv.remove(), 5000);
    }

    static displayTranslationResults(data, container) {
        const resultsContainer = document.getElementById(container);
        resultsContainer.innerHTML = '';

        // Display cost information
        const costDiv = document.createElement('div');
        costDiv.className = 'cost-info';
        costDiv.innerHTML = `
            <div class="cost-summary">
                <h4>Translation Cost Summary</h4>
                <div class="cost-grid">
                    <div class="cost-item">
                        <label>Total Cost:</label>
                        <span>$${data.cost_info.total_cost.toFixed(4)}</span>
                    </div>
                    <div class="cost-item">
                        <label>Input Cost:</label>
                        <span>$${data.cost_info.input_cost.toFixed(4)} (${data.cost_info.input_tokens} tokens)</span>
                    </div>
                    <div class="cost-item">
                        <label>Output Cost:</label>
                        <span>$${data.cost_info.output_cost.toFixed(4)} (${data.cost_info.output_tokens} tokens)</span>
                    </div>
                    <div class="cost-item">
                        <label>Model:</label>
                        <span>${data.cost_info.model}</span>
                    </div>
                </div>
            </div>
        `;
        resultsContainer.appendChild(costDiv);

        // Display original text
        const originalDiv = document.createElement('div');
        originalDiv.className = 'translation';
        originalDiv.innerHTML = `
            <h3>Original Text</h3>
            <p>${data.original_text}</p>
        `;
        resultsContainer.appendChild(originalDiv);

        // Display translations
        Object.entries(data.translations).forEach(([langCode, text]) => {
            const translationDiv = document.createElement('div');
            translationDiv.className = 'translation';
            translationDiv.innerHTML = `
                <h3>${Settings.getLanguageName(langCode)} Translation</h3>
                <p>${text}</p>
            `;
            resultsContainer.appendChild(translationDiv);
        });
    }

    static displayEvaluationResults(data) {
        const resultsDiv = document.getElementById('evaluation-results');
        
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
        
        const detailsHtml = data.results.map((result, index) => `
            <div class="result-card">
                <h4>Translation #${index + 1}</h4>
                <div class="translation-text">
                    <p><strong>Source:</strong> ${UI.escapeHtml(result.source_text)}</p>
                    <p><strong>Reference:</strong> ${UI.escapeHtml(result.reference_translation)}</p>
                    <p><strong>New Translation:</strong> ${UI.escapeHtml(result.new_translation)}</p>
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

    static escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}
