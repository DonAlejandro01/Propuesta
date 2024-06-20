document.addEventListener('DOMContentLoaded', function() {
    const compareForm = document.getElementById('compareForm');

    compareForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevenir el envío del formulario

        var audioFileInput = document.getElementById('audioFile');
        var pptFileInput = document.getElementById('pptFile');
        var comparisonResult = document.getElementById('comparisonResult');

        if (!audioFileInput.files.length || !pptFileInput.files.length) {
            comparisonResult.innerHTML = `<h2>Error:</h2><p>Por favor, suba ambos archivos de audio y PowerPoint.</p>`;
            return;
        }

        var container = document.getElementById('container');

        // Cambiar el contenido del contenedor a una animación de carga
        container.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Uploading files, please wait...</p>
                <p id="counter">0%</p>
            </div>
        `;

        var formData = new FormData(compareForm);

        fetch('/compare', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Restaurar el contenedor original
            container.innerHTML = `
                <h1>Upload files to compare</h1>
                <form id="compareForm" action="/compare" method="post" enctype="multipart/form-data">
                    <label for="audioFile">Audio File:</label>
                    <input type="file" name="audioFile" id="audioFile" accept="audio/*">
                    <label for="pptFile">PowerPoint File:</label>
                    <input type="file" name="pptFile" id="pptFile" accept=".ppt,.pptx">
                    <button type="submit" class="button">Upload</button>
                </form>
                <div id="comparisonResult"></div>
            `;
            
            comparisonResult = document.getElementById('comparisonResult');

            if (data.comparison) {
                comparisonResult.innerHTML = `<h2>Resultado de la comparación:</h2><p>${data.comparison}</p>`;
                
                if (data.references && data.references.length > 0) {
                    let referencesHtml = '<h3>Referencias:</h3><ul>';
                    data.references.forEach(reference => {
                        referencesHtml += `<li><a href="${reference.url}" target="_blank">${reference.text}</a></li>`;
                    });
                    referencesHtml += '</ul>';
                    comparisonResult.innerHTML += referencesHtml;
                }
            } else {
                comparisonResult.innerHTML = `<h2>Error:</h2><p>Error comparing the audio and PPT files</p>`;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `<h1>Error uploading the files: ${error.message}</h1>`;
        });
    });
});
