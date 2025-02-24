class Settings {
    static SUPPORTED_MODELS = [];

    static initializeModels = async () => {
        try {
            const response = await fetch('/api/models');
            if (!response.ok) {
                throw new Error('Failed to fetch models');
            }
            const data = await response.json();
            Settings.SUPPORTED_MODELS = data.models;
            return data.models;
        } catch (error) {
            console.error('Error fetching models:', error);
            return [];
        }
    }

    static SUPPORTED_LANGUAGES = [
        { code: 'es', name: 'Spanish' },
        { code: 'fr', name: 'French' },
        { code: 'de', name: 'German' },
        { code: 'ja', name: 'Japanese' },
        { code: 'ar', name: 'Arabic' },
        { code: 'hi', name: 'Hindi' },
        { code: 'pt', name: 'Portuguese' },
        { code: 'hu', name: 'Hungarian' }
    ];

    static getLanguageOptions() {
        return this.SUPPORTED_LANGUAGES.map(lang => 
            `<option value="${lang.code}">${lang.name}</option>`
        ).join('\n');
    }

    static getLanguageName(code) {
        const language = this.SUPPORTED_LANGUAGES.find(lang => lang.code === code);
        return language ? language.name : code;
    }

    static getModelOptions() {
        return this.SUPPORTED_MODELS.map(model => 
            `<option value="${model.id}" title="${model.description}">${model.name}</option>`
        ).join('\n');
    }

    static getModelConfig(modelId) {
        return this.SUPPORTED_MODELS.find(model => model.id === modelId);
    }
}
