class TranslationAPI {
    static async translateContent(endpoint, requestData) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Translation failed');
        }

        return await response.json();
    }

    static async evaluateTranslations(formData) {
        const response = await fetch('/api/evaluate-translations', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to evaluate translations');
        }

        return await response.json();
    }
}
