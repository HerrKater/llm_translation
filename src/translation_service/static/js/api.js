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
        console.log('Starting evaluation request...');
        console.log('FormData contents:');
        for (let [key, value] of formData.entries()) {
            console.log(key, ':', value);
        }
        const response = await fetch('/api/evaluate-translations', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error('Evaluation failed:', errorData);
            throw new Error(errorData?.detail || `Evaluation failed: ${response.status}`);
        }

        const data = await response.json();
        console.log('Raw evaluation response:', response);
        console.log('Parsed evaluation data:', data);
        console.log('Results array:', data.results);
        return data;
    }
}
