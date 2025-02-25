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
        
        // Extract both new and reference translation averages
        const metrics = [
            { key: 'accuracy', label: 'Accuracy' },
            { key: 'fluency', label: 'Fluency' },
            { key: 'adequacy', label: 'Adequacy' },
            { key: 'consistency', label: 'Consistency' },
            { key: 'contextual_appropriateness', label: 'Contextual Appropriateness' },
            { key: 'terminology_accuracy', label: 'Terminology Accuracy' },
            { key: 'readability', label: 'Readability' },
            { key: 'format_preservation', label: 'Format Preservation' },
            { key: 'error_rate', label: 'Error Rate' }
        ];

        // Create comparison rows
        const comparisonRows = metrics.map(metric => {
            const newScore = data.summary[`avg_${metric.key}`];
            const refScore = data.summary[`avg_reference_${metric.key}`];
            const diff = newScore - refScore;
            const diffColor = diff > 0 ? '#28a745' : diff < 0 ? '#dc3545' : '#6c757d';
            const diffSymbol = diff > 0 ? '▲' : diff < 0 ? '▼' : '=';
            
            return `
                <tr>
                    <td>${metric.label}</td>
                    <td class="score-cell">
                        <div class="score-comparison">
                            <div class="ref-score" title="Reference Score">${refScore.toFixed(1)}</div>
                            <div class="score-arrow" style="color: ${diffColor}">${diffSymbol}</div>
                            <div class="new-score" title="New Score">${newScore.toFixed(1)}</div>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');

        const summaryHtml = `
            <div class="summary-card">
                <h3>Evaluation Summary</h3>
                <div class="legend">
                    <div class="legend-item">
                        <span class="legend-label">Reference Score</span>
                        <span class="legend-arrow">→</span>
                        <span class="legend-label">New Score</span>
                    </div>
                    <div class="legend-item">
                        <span style="color: #28a745">▲</span> Better
                        <span style="color: #dc3545">▼</span> Worse
                        <span style="color: #6c757d">=</span> Same
                    </div>
                </div>
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Scores Comparison</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${comparisonRows}
                    </tbody>
                </table>
            </div>
            <style>
                .legend {
                    margin: 10px 0;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }
                .legend-item {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    margin: 5px 0;
                    font-size: 0.9em;
                }
                .legend-arrow {
                    color: #6c757d;
                }
                .score-cell {
                    min-width: 150px;
                }
                .score-comparison {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    justify-content: center;
                }
                .ref-score {
                    color: #666;
                }
                .new-score {
                    font-weight: bold;
                }
                .score-arrow {
                    font-size: 1.2em;
                }
            </style>
        `;

        // Generate the detailed results HTML for each evaluation
        const detailsHtml = data.results.map(result => `
            <div class="evaluation-result">
                <h4>Translation Evaluation</h4>
                <div class="text-samples">
                    <div class="text-sample">
                        <h5>Original Text</h5>
                        <p>${result.original_text}</p>
                    </div>
                    <div class="text-sample">
                        <h5>Reference Translation</h5>
                        <p>${result.reference_translation}</p>
                    </div>
                    <div class="text-sample">
                        <h5>New Translation</h5>
                        <p>${result.new_translation}</p>
                    </div>
                </div>

                <div class="evaluation-details">
                    <h5>Evaluation Details</h5>
                    <div class="evaluation-tables">
                        <div class="reference-evaluation">
                            <h6>Reference Translation Evaluation</h6>
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
                        </div>
                        
                        <div class="new-evaluation">
                            <h6>New Translation Evaluation</h6>
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
                    </div>
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
                    <p>${result.new_evaluation.comments}</p>
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