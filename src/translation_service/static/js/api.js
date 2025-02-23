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
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Translation failed: ${response.status}`);
        }

        return await response.json();
    }

    static async evaluateTranslations(formData) {
        const response = await fetch('/api/evaluate-translations', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(errorData?.detail || `Evaluation failed: ${response.status}`);
        }

        return await response.json();
    }
}
