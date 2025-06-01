/**
 * CV Forms JavaScript
 * Handles autocomplete, dynamic forms, and skill selection for PickleCV creation
 */

class CVFormsManager {
    constructor() {
        this.autocompleteCache = new Map();
        this.experienceCount = 1;
        this.educationCount = 1;
        
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeAutocomplete();
            this.initializeSkillSelection();
            this.initializeDynamicForms();
        });
    }

    // ==================== AUTOCOMPLETE FUNCTIONALITY ====================

    initializeAutocomplete() {
        // Company autocomplete
        this.setupAutocomplete('.autocomplete-company', '/employment/api/companies/autocomplete/');
        
        // Location autocomplete
        this.setupAutocomplete('.autocomplete-location', '/employment/api/locations/autocomplete/');
        
        // School autocomplete
        this.setupAutocomplete('.autocomplete-school', '/employment/api/schools/autocomplete/');
    }

    setupAutocomplete(selector, apiUrl) {
        document.querySelectorAll(selector).forEach(input => {
            let currentSuggestions = [];
            let selectedIndex = -1;
            let timeoutId = null;
            let abortController = null;
            
            // Find the suggestions container for this input
            const container = input.closest('.autocomplete-container');
            const suggestionsDiv = container.querySelector('.autocomplete-suggestions');
            
            input.addEventListener('input', (e) => {
                const query = e.target.value.trim();
                
                // Clear existing timeout and abort pending requests
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }
                if (abortController) {
                    abortController.abort();
                }
                
                if (query.length < 2) {
                    this.hideSuggestions(suggestionsDiv);
                    currentSuggestions = [];
                    selectedIndex = -1;
                    return;
                }
                
                // Check cache first
                const cacheKey = `${apiUrl}:${query.toLowerCase()}`;
                if (this.autocompleteCache.has(cacheKey)) {
                    currentSuggestions = this.autocompleteCache.get(cacheKey);
                    selectedIndex = -1;
                    this.showSuggestions(suggestionsDiv, currentSuggestions, input);
                    return;
                }
                
                // Debounced API call
                timeoutId = setTimeout(() => {
                    abortController = new AbortController();
                    
                    fetch(`${apiUrl}?term=${encodeURIComponent(query)}`, {
                        signal: abortController.signal
                    })
                        .then(response => response.json())
                        .then(suggestions => {
                            // Cache the result
                            this.autocompleteCache.set(cacheKey, suggestions);
                            
                            // Limit cache size to prevent memory issues
                            if (this.autocompleteCache.size > 100) {
                                const firstKey = this.autocompleteCache.keys().next().value;
                                this.autocompleteCache.delete(firstKey);
                            }
                            
                            currentSuggestions = suggestions;
                            selectedIndex = -1;
                            this.showSuggestions(suggestionsDiv, suggestions, input);
                        })
                        .catch(error => {
                            if (error.name !== 'AbortError') {
                                console.error('Autocomplete error:', error);
                                this.hideSuggestions(suggestionsDiv);
                            }
                        });
                }, 150);
            });
            
            input.addEventListener('keydown', (e) => {
                if (currentSuggestions.length === 0) return;
                
                switch (e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        selectedIndex = Math.min(selectedIndex + 1, currentSuggestions.length - 1);
                        this.updateSelectedSuggestion(suggestionsDiv, selectedIndex);
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        selectedIndex = Math.max(selectedIndex - 1, -1);
                        this.updateSelectedSuggestion(suggestionsDiv, selectedIndex);
                        break;
                    case 'Enter':
                        e.preventDefault();
                        if (selectedIndex >= 0) {
                            this.selectSuggestion(input, currentSuggestions[selectedIndex], suggestionsDiv);
                        }
                        break;
                    case 'Escape':
                        this.hideSuggestions(suggestionsDiv);
                        currentSuggestions = [];
                        selectedIndex = -1;
                        break;
                }
            });
            
            input.addEventListener('blur', () => {
                setTimeout(() => {
                    this.hideSuggestions(suggestionsDiv);
                }, 150);
            });
        });
    }

    showSuggestions(suggestionsDiv, suggestions, input) {
        if (suggestions.length === 0) {
            this.hideSuggestions(suggestionsDiv);
            return;
        }
        
        // Use DocumentFragment for better performance
        const fragment = document.createDocumentFragment();
        suggestions.forEach((suggestion) => {
            const div = document.createElement('div');
            div.className = 'autocomplete-suggestion';
            div.textContent = suggestion.value;
            div.addEventListener('click', () => {
                this.selectSuggestion(input, suggestion, suggestionsDiv);
            });
            fragment.appendChild(div);
        });
        
        suggestionsDiv.innerHTML = '';
        suggestionsDiv.appendChild(fragment);
        suggestionsDiv.style.display = 'block';
    }

    hideSuggestions(suggestionsDiv) {
        suggestionsDiv.style.display = 'none';
    }

    updateSelectedSuggestion(suggestionsDiv, selectedIndex) {
        const suggestions = suggestionsDiv.querySelectorAll('.autocomplete-suggestion');
        suggestions.forEach((sugg, index) => {
            sugg.classList.toggle('selected', index === selectedIndex);
        });
    }

    selectSuggestion(input, suggestion, suggestionsDiv) {
        input.value = suggestion.value;
        this.hideSuggestions(suggestionsDiv);
        input.focus();
    }

    // ==================== SKILL SELECTION FUNCTIONALITY ====================

    initializeSkillSelection() {
        this.handleSkillSelection();
    }

    handleSkillSelection() {
        // Handle skill selection for all skill grids
        document.querySelectorAll('.skills-grid').forEach(grid => {
            grid.querySelectorAll('.skill-item').forEach(item => {
                const checkbox = item.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    // Set initial state
                    item.classList.toggle('selected', checkbox.checked);
                    
                    // Remove existing event listeners to prevent duplicates
                    const newItem = item.cloneNode(true);
                    item.parentNode.replaceChild(newItem, item);
                }
            });
        });
        
        // Re-attach event listeners to all skill items
        document.querySelectorAll('.skill-item').forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox) {
                item.addEventListener('click', (event) => {
                    if (event.target !== checkbox && !checkbox.contains(event.target)) {
                        checkbox.checked = !checkbox.checked;
                    }
                    item.classList.toggle('selected', checkbox.checked);
                });
            }
        });

        // Handle interest selection
        document.querySelectorAll('.interest-item').forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox) {
                item.classList.toggle('selected', checkbox.checked);
                item.addEventListener('click', (event) => {
                    if (event.target !== checkbox && !checkbox.contains(event.target)) {
                        checkbox.checked = !checkbox.checked;
                    }
                    item.classList.toggle('selected', checkbox.checked);
                });
            }
        });
    }

    // ==================== DYNAMIC FORM FUNCTIONALITY ====================

    initializeDynamicForms() {
        // Experience forms
        const addExperienceBtn = document.getElementById('add-experience');
        if (addExperienceBtn) {
            addExperienceBtn.addEventListener('click', () => this.addExperienceForm());
        }

        // Education forms
        const addEducationBtn = document.getElementById('add-education');
        if (addEducationBtn) {
            addEducationBtn.addEventListener('click', () => this.addEducationForm());
        }

        this.updateRemoveButtons();
    }

    addExperienceForm() {
        this.experienceCount++;
        const template = document.querySelector('.experience-form').cloneNode(true);
        
        // Update form numbering and IDs
        template.querySelector('h3').textContent = 'Experience #' + this.experienceCount;
        template.querySelector('.remove-experience').style.display = 'block';
        
        // Update all input IDs and names
        this.updateFormFields(template, this.experienceCount - 1);
        
        // Update suggestion container IDs
        this.updateSuggestionContainers(template, this.experienceCount - 1);
        
        // Reset skill selections
        template.querySelectorAll('.skill-item').forEach(item => {
            item.classList.remove('selected');
        });
        
        document.getElementById('experience-forms').appendChild(template);
        this.updateRemoveButtons();
        this.initializeSkillSelection();
        this.initializeAutocomplete();
    }

    addEducationForm() {
        this.educationCount++;
        const template = document.querySelector('.education-form').cloneNode(true);
        
        // Update form numbering and IDs
        template.querySelector('h3').textContent = 'Education #' + this.educationCount;
        template.querySelector('.remove-education').style.display = 'block';
        
        // Update all input IDs and names
        this.updateFormFields(template, this.educationCount - 1);
        
        document.getElementById('education-forms').appendChild(template);
        this.updateRemoveButtons();
        this.initializeAutocomplete();
    }

    updateFormFields(template, index) {
        const inputs = template.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const name = input.name;
            const id = input.id;
            if (name) {
                input.name = name.replace(/_\d+$/, '_' + index);
            }
            if (id) {
                input.id = id.replace(/_\d+$/, '_' + index);
            }
            input.value = '';
            if (input.type === 'checkbox') {
                input.checked = false;
            }
        });

        // Update skill checkboxes specifically
        const skillCheckboxes = template.querySelectorAll('input[name^="skills_"]');
        skillCheckboxes.forEach(checkbox => {
            checkbox.name = 'skills_' + index;
            checkbox.id = checkbox.id.replace(/_\d+$/, '_' + index);
            checkbox.checked = false;
        });
    }

    updateSuggestionContainers(template, index) {
        const employerSuggestions = template.querySelector('[id^="employer-suggestions"]');
        const locationSuggestions = template.querySelector('[id^="location-suggestions"]');
        if (employerSuggestions) {
            employerSuggestions.id = `employer-suggestions-${index}`;
        }
        if (locationSuggestions) {
            locationSuggestions.id = `location-suggestions-${index}`;
        }
    }

    updateRemoveButtons() {
        document.querySelectorAll('.remove-experience').forEach(button => {
            // Remove existing event listeners
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', () => {
                if (document.querySelectorAll('.experience-form').length > 1) {
                    newButton.closest('.experience-form').remove();
                    this.updateExperienceFormNumbers();
                }
            });
        });

        document.querySelectorAll('.remove-education').forEach(button => {
            // Remove existing event listeners
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            newButton.addEventListener('click', () => {
                if (document.querySelectorAll('.education-form').length > 1) {
                    newButton.closest('.education-form').remove();
                    this.updateEducationFormNumbers();
                }
            });
        });
    }

    updateExperienceFormNumbers() {
        document.querySelectorAll('.experience-form').forEach((form, index) => {
            form.querySelector('h3').textContent = 'Experience #' + (index + 1);
            this.updateFormFields(form, index);
        });
    }

    updateEducationFormNumbers() {
        document.querySelectorAll('.education-form').forEach((form, index) => {
            form.querySelector('h3').textContent = 'Education #' + (index + 1);
            this.updateFormFields(form, index);
        });
    }
}

// Initialize the CV Forms Manager
const cvFormsManager = new CVFormsManager(); 