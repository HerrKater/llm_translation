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
        console.log('Displaying evaluation results:', JSON.stringify(data, null, 2));
        const resultsDiv = document.getElementById('evaluation-results');
        if (!resultsDiv) {
            console.error('Could not find evaluation-results div');
            return;
        }
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        
        if (!data || !data.summary) {
            console.error('Invalid data structure - missing summary:', data);
            UI.showError('Invalid response format from server');
            return;
        }
        
        const metricAverages = {
            accuracy: data.summary.avg_accuracy,
            fluency: data.summary.avg_fluency,
            adequacy: data.summary.avg_adequacy,
            consistency: data.summary.avg_consistency,
            contextual_appropriateness: data.summary.avg_contextual_appropriateness,
            terminology_accuracy: data.summary.avg_terminology_accuracy,
            readability: data.summary.avg_readability,
            format_preservation: data.summary.avg_format_preservation,
            error_rate: data.summary.avg_error_rate
        };
        
        console.log('Metric averages:', metricAverages);

        console.log('Generating summary HTML with metrics:', metricAverages);
        const summaryHtml = `
            <div class="summary-card">
                <h3>Evaluation Summary</h3>
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Average Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Accuracy</td>
                            <td>${metricAverages.accuracy}/5</td>
                        </tr>
                        <tr>
                            <td>Fluency</td>
                            <td>${metricAverages.fluency}/5</td>
                        </tr>
                        <tr>
                            <td>Adequacy</td>
                            <td>${metricAverages.adequacy}/5</td>
                        </tr>
                        <tr>
                            <td>Consistency</td>
                            <td>${metricAverages.consistency}/5</td>
                        </tr>
                        <tr>
                            <td>Contextual Appropriateness</td>
                            <td>${metricAverages.contextual_appropriateness}/5</td>
                        </tr>
                        <tr>
                            <td>Terminology Accuracy</td>
                            <td>${metricAverages.terminology_accuracy}/5</td>
                        </tr>
                        <tr>
                            <td>Readability</td>
                            <td>${metricAverages.readability}/5</td>
                        </tr>
                        <tr>
                            <td>Format Preservation</td>
                            <td>${metricAverages.format_preservation}/5</td>
                        </tr>
                        <tr>
                            <td>Error Rate</td>
                            <td>${metricAverages.error_rate}/5</td>
                        </tr>
                    </tbody>
                </table>
                <div class="total-cost">
                    <label>Total Cost</label>
                    <span>$${data.total_cost.toFixed(6)}</span>
                </div>
            </div>
        `;
        
        console.log('Generating details HTML for results:', data.results);
        const detailsHtml = data.results.map((result, index) => `
            <div class="result-card">
                <h4>Translation #${index + 1}</h4>
                <div class="translation-text">
                    <p><strong>Source:</strong> ${UI.escapeHtml(result.source_text)}</p>
                    <p><strong>Reference:</strong> ${UI.escapeHtml(result.reference_translation)}</p>
                    <p><strong>New Translation:</strong> ${UI.escapeHtml(result.new_translation)}</p>
                </div>
                <div class="metrics-details">
                    <h5>Reference Translation Evaluation</h5>
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Score</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Accuracy</td>
                                <td>${result.reference_evaluation.accuracy.score}/5</td>
                                <td>${result.reference_evaluation.accuracy.explanation}</td>
                            </tr>
                            <tr>
                                <td>Fluency</td>
                                <td>${result.reference_evaluation.fluency.score}/5</td>
                                <td>${result.reference_evaluation.fluency.explanation}</td>
                            </tr>
                            <tr>
                                <td>Adequacy</td>
                                <td>${result.reference_evaluation.adequacy.score}/5</td>
                                <td>${result.reference_evaluation.adequacy.explanation}</td>
                            </tr>
                            <tr>
                                <td>Consistency</td>
                                <td>${result.reference_evaluation.consistency.score}/5</td>
                                <td>${result.reference_evaluation.consistency.explanation}</td>
                            </tr>
                            <tr>
                                <td>Contextual Appropriateness</td>
                                <td>${result.reference_evaluation.contextual_appropriateness.score}/5</td>
                                <td>${result.reference_evaluation.contextual_appropriateness.explanation}</td>
                            </tr>
                            <tr>
                                <td>Terminology Accuracy</td>
                                <td>${result.reference_evaluation.terminology_accuracy.score}/5</td>
                                <td>${result.reference_evaluation.terminology_accuracy.explanation}</td>
                            </tr>
                            <tr>
                                <td>Readability</td>
                                <td>${result.reference_evaluation.readability.score}/5</td>
                                <td>${result.reference_evaluation.readability.explanation}</td>
                            </tr>
                            <tr>
                                <td>Format Preservation</td>
                                <td>${result.reference_evaluation.format_preservation.score}/5</td>
                                <td>${result.reference_evaluation.format_preservation.explanation}</td>
                            </tr>
                            <tr>
                                <td>Error Rate</td>
                                <td>${result.reference_evaluation.error_rate.score}/5</td>
                                <td>${result.reference_evaluation.error_rate.explanation}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <h5>New Translation Evaluation</h5>
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Metric</th>
                                <th>Score</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Accuracy</td>
                                <td>${result.new_evaluation.accuracy.score}/5</td>
                                <td>${result.new_evaluation.accuracy.explanation}</td>
                            </tr>
                            <tr>
                                <td>Fluency</td>
                                <td>${result.new_evaluation.fluency.score}/5</td>
                                <td>${result.new_evaluation.fluency.explanation}</td>
                            </tr>
                            <tr>
                                <td>Adequacy</td>
                                <td>${result.new_evaluation.adequacy.score}/5</td>
                                <td>${result.new_evaluation.adequacy.explanation}</td>
                            </tr>
                            <tr>
                                <td>Consistency</td>
                                <td>${result.new_evaluation.consistency.score}/5</td>
                                <td>${result.new_evaluation.consistency.explanation}</td>
                            </tr>
                            <tr>
                                <td>Contextual Appropriateness</td>
                                <td>${result.new_evaluation.contextual_appropriateness.score}/5</td>
                                <td>${result.new_evaluation.contextual_appropriateness.explanation}</td>
                            </tr>
                            <tr>
                                <td>Terminology Accuracy</td>
                                <td>${result.new_evaluation.terminology_accuracy.score}/5</td>
                                <td>${result.new_evaluation.terminology_accuracy.explanation}</td>
                            </tr>
                            <tr>
                                <td>Readability</td>
                                <td>${result.new_evaluation.readability.score}/5</td>
                                <td>${result.new_evaluation.readability.explanation}</td>
                            </tr>
                            <tr>
                                <td>Format Preservation</td>
                                <td>${result.new_evaluation.format_preservation.score}/5</td>
                                <td>${result.new_evaluation.format_preservation.explanation}</td>
                            </tr>
                            <tr>
                                <td>Error Rate</td>
                                <td>${result.new_evaluation.error_rate.score}/5</td>
                                <td>${result.new_evaluation.error_rate.explanation}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="cost-section">
                    <h5>Evaluation Cost</h5>
                    <div class="cost-details">
                        <div class="cost-item">
                            <label>Total:</label>
                            <span>$${result.cost_info.total_cost.toFixed(4)}</span>
                        </div>
                        <div class="cost-item">
                            <label>Input:</label>
                            <span>$${result.cost_info.input_cost.toFixed(4)} (${result.cost_info.input_tokens} tokens)</span>
                        </div>
                        <div class="cost-item">
                            <label>Output:</label>
                            <span>$${result.cost_info.output_cost.toFixed(4)} (${result.cost_info.output_tokens} tokens)</span>
                        </div>
                        <div class="cost-item">
                            <label>Model:</label>
                            <span>${result.cost_info.model}</span>
                        </div>
                    </div>
                </div>
                <div class="comments">
                    <strong>Comments:</strong>
                    <p>${result.comments}</p>
                </div>
            </div>
        `).join('');
        
        const finalHtml = summaryHtml + detailsHtml;
        console.log('Setting final HTML:', finalHtml);
        resultsDiv.innerHTML = finalHtml;
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
