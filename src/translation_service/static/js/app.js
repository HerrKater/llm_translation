class TranslationApp {
    constructor() {
        this.initialize().catch(error => {
            console.error('Failed to initialize app:', error);
        });
    }

    async initialize() {
        try {
            await Settings.initializeModels();
            this.initializeEventListeners();
            this.initializeSelect2();
        } catch (error) {
            console.error('Error during initialization:', error);
            throw error;
        }
    }

    initializeEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        // Model selection change handlers
        $('#translation-model').on('change', (e) => this.updateModelInfo('translation', e.target.value));
        $('#evaluation-model').on('change', (e) => this.updateModelInfo('evaluation', e.target.value));
        $('#text-translation-model').on('change', (e) => this.updateModelInfo('text-translation', e.target.value));

        // Initialize model info
        this.updateModelInfo('translation', $('#translation-model').val());
        this.updateModelInfo('evaluation', $('#evaluation-model').val());
        this.updateModelInfo('text-translation', $('#text-translation-model').val());

        // Translation buttons
        document.getElementById('translateUrlButton')?.addEventListener('click', () => this.handleUrlTranslation());
        document.getElementById('translateTextButton')?.addEventListener('click', () => this.handleTextTranslation());
        document.getElementById('evaluateButton')?.addEventListener('click', (e) => this.handleEvaluation(e));

        // Form validation
        document.getElementById('url')?.addEventListener('input', (e) => {
            try {
                if (e.target.value) new URL(e.target.value);
                e.target.setCustomValidity('');
            } catch {
                e.target.setCustomValidity('Please enter a valid URL');
            }
        });
    }

    initializeSelect2() {
        // Populate language options
        const languageOptions = Settings.getLanguageOptions();
        $('#url-languages, #text-languages, #evaluation-language').html(languageOptions);

        // Populate model options
        const modelOptions = Settings.getModelOptions();
        $('#translation-model, #evaluation-model, #text-translation-model').html(modelOptions);

        // Initialize Select2 for translation tabs
        $('#url-languages, #text-languages').select2({
            placeholder: 'Select target languages',
            width: '100%'
        });

        // Initialize Select2 for evaluation tab
        $('#evaluation-language').select2({
            placeholder: 'Select target language',
            width: '100%'
        });
    }

    switchTab(tabId) {
        // Update tab active states
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabId);
        });

        // Update content visibility
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === tabId);
        });
    }

    updateModelInfo(type, modelId) {
        if (!modelId) return;

        const model = Settings.getModelConfig(modelId);
        if (!model) return;

        const infoDiv = document.getElementById(`${type}-model-info`);
        infoDiv.innerHTML = `
            <div class="description">${model.description}</div>
            <div class="costs">
                <div class="cost-item">
                    <label>Input Cost</label>
                    $${model.inputCost.toFixed(3)}/1K tokens
                </div>
                <div class="cost-item">
                    <label>Output Cost</label>
                    $${model.outputCost.toFixed(3)}/1K tokens
                </div>
            </div>
        `;
    }

    async handleUrlTranslation() {
        const url = document.getElementById('url').value.trim();
        const languages = $('#url-languages').val();

        if (!url) {
            UI.showError('Please enter a URL');
            return;
        }

        if (languages.length === 0) {
            UI.showError('Please select at least one target language');
            return;
        }

        try {
            // Validate URL format
            new URL(url);
            
            UI.showLoading('Translating... Please wait...');
            const result = await TranslationAPI.translateContent('/translate', {
                url,
                target_languages: languages
            });
            UI.displayTranslationResults(result, 'url-results');
        } catch (error) {
            if (error instanceof TypeError) {
                UI.showError('Please enter a valid URL (e.g., https://example.com)');
            } else {
                UI.showError(error.message);
            }
        } finally {
            UI.hideLoading();
        }
    }

    async handleTextTranslation() {
        const text = document.getElementById('raw-text').value.trim();
        const languages = $('#text-languages').val();
        const model = $('#text-translation-model').val();

        if (!text) {
            UI.showError('Please enter some text');
            return;
        }

        if (languages.length === 0) {
            UI.showError('Please select at least one target language');
            return;
        }

        try {
            UI.showLoading('Translating... Please wait...');
            const result = await TranslationAPI.translateContent('/translate/raw', {
                text,
                target_languages: languages,
                model: model
            });
            UI.displayTranslationResults(result, 'text-results');
        } catch (error) {
            UI.showError(error.message);
        } finally {
            UI.hideLoading();
        }
    }

    async handleEvaluation(event) {
        event.preventDefault();
        
        const fileInput = document.getElementById('csv-file');
        const file = fileInput.files[0];
        const targetLanguage = $('#evaluation-language').val();
        const translationModel = $('#translation-model').val();
        const evaluationModel = $('#evaluation-model').val();
        
        if (!file) {
            UI.showError('Please select a CSV file');
            return;
        }

        if (!targetLanguage) {
            UI.showError('Please select a target language');
            return;
        }

        if (!translationModel) {
            UI.showError('Please select a translation model');
            return;
        }

        if (!evaluationModel) {
            UI.showError('Please select an evaluation model');
            return;
        }

        // Validate file type
        if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
            UI.showError('Please select a valid CSV file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('target_language', targetLanguage);
        formData.append('translation_model', translationModel);
        formData.append('evaluation_model', evaluationModel);
        
        try {
            UI.showLoading('Evaluating translations...');
            const result = await TranslationAPI.evaluateTranslations(formData);
            console.log('Received evaluation result:', result);
            UI.displayEvaluationResults(result);
        } catch (error) {
            UI.showError(error.message);
        } finally {
            UI.hideLoading();
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TranslationApp();
});
