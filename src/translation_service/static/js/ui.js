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
        
        // Add CSS for the updated UI
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .pagination-controls {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin: 15px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            .pagination-btn {
                padding: 8px 15px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .pagination-btn:disabled {
                background: #6c757d;
                cursor: not-allowed;
            }
            .pagination-info {
                font-weight: bold;
            }
            .metrics-comparison-table {
                width: 100%;
                border-collapse: collapse;
            }
            .metrics-comparison-table th, 
            .metrics-comparison-table td {
                padding: 10px;
                border: 1px solid #dee2e6;
            }
            .metrics-comparison-table th {
                background-color: #f8f9fa;
            }
            .ref-score {
                color: #666;
                text-align: center;
            }
            .new-score {
                font-weight: bold;
                text-align: center;
            }
            .score-arrow {
                font-size: 1.2em;
                text-align: center;
            }
            .toggle-btn {
                padding: 5px 10px;
                background: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                cursor: pointer;
            }
            .metric-details {
                margin-top: 10px;
                padding: 10px;
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            .detail-section {
                margin-bottom: 10px;
            }
            .detail-section h6 {
                margin-bottom: 5px;
                font-weight: bold;
            }
            .metrics-legend {
                display: flex;
                gap: 15px;
                margin-bottom: 10px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            .legend-item {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            .evaluation-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
            .evaluation-header h4 {
                margin: 0;
            }
            @media (max-width: 768px) {
                .evaluation-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 10px;
                }
                .pagination-controls {
                    width: 100%;
                }
            }
        `;
        document.head.appendChild(styleElement);
        
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

        // Generate pagination controls
        const createPaginationControls = (currentPage, totalPages) => {
            let paginationHtml = `
                <div class="pagination-controls">
                    <button class="pagination-btn prev-btn" ${currentPage <= 1 ? 'disabled' : ''} data-page="${currentPage - 1}">« Previous</button>
                    <span class="pagination-info">Translation ${currentPage} of ${totalPages}</span>
                    <button class="pagination-btn next-btn" ${currentPage >= totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">Next »</button>
                </div>
            `;
            return paginationHtml;
        };
        
        // Generate the detailed results HTML for each evaluation
        const resultDetailsList = data.results.map((result, index) => {
            // Create comparison rows for the detailed metrics
            const metricComparisons = metrics.map(metric => {
                const refScore = result.reference_evaluation[metric.key].score;
                const newScore = result.new_evaluation[metric.key].score;
                const diff = newScore - refScore;
                const diffColor = diff > 0 ? '#28a745' : diff < 0 ? '#dc3545' : '#6c757d';
                const diffSymbol = diff > 0 ? '▲' : diff < 0 ? '▼' : '=';
                
                return `
                    <tr>
                        <td>${metric.label}</td>
                        <td class="score-cell ref-score">${refScore}/5</td>
                        <td class="score-arrow" style="color: ${diffColor}">${diffSymbol}</td>
                        <td class="score-cell new-score">${newScore}/5</td>
                        <td class="details-cell toggle-details" data-metric="${metric.key}">
                            <button class="toggle-btn">View Details</button>
                            <div class="metric-details" style="display: none;">
                                <div class="detail-section">
                                    <h6>Reference:</h6>
                                    <p>${result.reference_evaluation[metric.key].explanation}</p>
                                </div>
                                <div class="detail-section">
                                    <h6>New:</h6>
                                    <p>${result.new_evaluation[metric.key].explanation}</p>
                                </div>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');

            return `
                <div class="evaluation-result" id="evaluation-${index+1}" style="display: ${index === 0 ? 'block' : 'none'};">
                    <div class="evaluation-header">
                        <h4>Translation Evaluation ${index + 1}</h4>
                        ${createPaginationControls(index + 1, data.results.length)}
                    </div>
                    
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
                        <h5>Evaluation Metrics Comparison</h5>
                        <div class="metrics-legend">
                            <div class="legend-item"><span style="color: #28a745">▲</span> New translation scores higher</div>
                            <div class="legend-item"><span style="color: #dc3545">▼</span> New translation scores lower</div>
                            <div class="legend-item"><span style="color: #6c757d">=</span> Scores are equal</div>
                        </div>
                        <table class="metrics-comparison-table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Reference</th>
                                    <th></th>
                                    <th>New</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${metricComparisons}
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="cost-section">
                        <h5>Evaluation Cost</h5>
                        <div class="cost-details">
                            <div class="cost-item">
                                <label>Total:</label>
                                <span>${result.cost_info.total_cost.toFixed(4)}</span>
                            </div>
                            <div class="cost-item">
                                <label>Input:</label>
                                <span>${result.cost_info.input_cost.toFixed(4)} (${result.cost_info.input_tokens} tokens)</span>
                            </div>
                            <div class="cost-item">
                                <label>Output:</label>
                                <span>${result.cost_info.output_cost.toFixed(4)} (${result.cost_info.output_tokens} tokens)</span>
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
                    ${createPaginationControls(index + 1, data.results.length)}
                </div>
            `;
        });
        
        const detailsHtml = resultDetailsList.join('');
        const finalHtml = summaryHtml + detailsHtml;
        
        console.log('Setting final HTML:', finalHtml);
        resultsDiv.innerHTML = finalHtml;
        
        // Add event listeners for pagination
        setTimeout(() => {
            const paginationButtons = document.querySelectorAll('.pagination-btn');
            paginationButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const targetPage = parseInt(this.dataset.page);
                    if (!isNaN(targetPage)) {
                        // Hide all evaluation results
                        document.querySelectorAll('.evaluation-result').forEach(result => {
                            result.style.display = 'none';
                        });
                        
                        // Show the selected result
                        const targetResult = document.getElementById(`evaluation-${targetPage}`);
                        if (targetResult) {
                            targetResult.style.display = 'block';
                            // Scroll to the top of the result
                            targetResult.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                });
            });
            
            // Add event listeners for metric detail toggles
            document.querySelectorAll('.toggle-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const detailsDiv = this.parentElement.querySelector('.metric-details');
                    if (detailsDiv.style.display === 'none') {
                        detailsDiv.style.display = 'block';
                        this.textContent = 'Hide Details';
                    } else {
                        detailsDiv.style.display = 'none';
                        this.textContent = 'View Details';
                    }
                });
            });
        }, 100);
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