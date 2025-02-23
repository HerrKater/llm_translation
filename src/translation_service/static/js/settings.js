class Settings {
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
}
