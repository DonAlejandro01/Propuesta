document.addEventListener('DOMContentLoaded', () => {
    const pptInput = document.getElementById('pptInput');
    const audioInput = document.getElementById('audioInput');
    const pptFileNameDiv = document.getElementById('pptFileName');
    const audioFileNameDiv = document.getElementById('audioFileName');
    const analysisButton = document.getElementById('analysisButton');
    const uploadContainer = document.querySelector('.upload-container');
    const suggestionsSection = document.querySelector('.Suggestions');
    const slideTitle = document.querySelector('.titulo_Diapo');
    const slideContent = document.querySelector('.Suggestions ul');
    const prevButton = document.querySelector('.buttons button:nth-child(1)');
    const nextButton = document.querySelector('.buttons button:nth-child(2)');
    const coloresSugDiv = document.querySelector('.colores-sug');

    let slides = [];
    let currentSlideIndex = 0;

    const truncateText = (text, maxLength) => {
        if (text.length > maxLength) {
            return text.substring(0, maxLength) + '... <a href="#" class="show-more">ver más</a>';
        }
        return text;
    };

    const updateSlideContent = (index) => {
        if (slides.length > 0) {
            slideTitle.textContent = slides[index].slide_number ? `Diapositiva ${slides[index].slide_number}` : `Diapositiva ${index + 1}`;
            const suggestions = Array.isArray(slides[index].suggestions) ? slides[index].suggestions : [slides[index].suggestions];
            slideContent.innerHTML = suggestions.map(item => `<li>${truncateText(item, 200)}</li>`).join('');

            document.querySelectorAll('.show-more').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    link.parentElement.innerHTML = suggestions[link.parentElement.index];
                });
            });
        }
    };

    const fetchSuggestions = () => {
        const formData = new FormData();
        formData.append('pptFile', pptInput.files[0]);

        fetch('/compare', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.results) {
                slides = data.results;
                currentSlideIndex = 0; // Reiniciar el índice de la diapositiva actual
                updateSlideContent(currentSlideIndex);
                uploadContainer.style.display = 'none';
                suggestionsSection.style.display = 'flex';
                fetchColors(); // Llamar a la función para obtener y mostrar los colores
            } else {
                console.error('No results in response');
            }
        })
        .catch(error => console.error('Error fetching suggestions:', error));
    };

    const fetchColors = () => {
        const formData = new FormData();
        formData.append('pptFile', pptInput.files[0]);

        fetch('/get_colors', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (Array.isArray(data.colors)) {
                updateColors(data.colors); // Mostrar los colores sugeridos
            } else {
                console.error('Colors response is not an array');
            }
        })
        .catch(error => console.error('Error fetching colors:', error));
    };

    const updateColors = (colors) => {
        coloresSugDiv.innerHTML = colors.map(color => {
            const [colorName, hex] = color.split(' (#');
            return `<div style="background-color:#${hex.replace(')', '')}; width:100px; height:50px;" title="${colorName.trim()}"></div>`;
        }).join('');
    };

    pptInput.addEventListener('change', () => {
        const fileName = pptInput.files[0]?.name || 'No file chosen';
        pptFileNameDiv.textContent = fileName;
        pptFileNameDiv.classList.remove('hidden');
    });

    audioInput.addEventListener('change', () => {
        const fileName = audioInput.files[0]?.name || 'No file chosen';
        audioFileNameDiv.textContent = fileName;
        audioFileNameDiv.classList.remove('hidden');
    });

    analysisButton.addEventListener('click', fetchSuggestions);

    prevButton.addEventListener('click', () => {
        if (currentSlideIndex > 0) {
            currentSlideIndex--;
            updateSlideContent(currentSlideIndex);
        }
    });

    nextButton.addEventListener('click', () => {
        if (currentSlideIndex < slides.length - 1) {
            currentSlideIndex++;
            updateSlideContent(currentSlideIndex);
        }
    });
});
