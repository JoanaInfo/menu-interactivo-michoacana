document.addEventListener('DOMContentLoaded', () => {
    const welcomeScreen = document.getElementById('welcome-screen');
    const startButton = document.getElementById('start-button');
    const quizContainer = document.getElementById('quiz-container');
    const questionContainers = document.querySelectorAll('.question-container');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('recommendation-result');

    let currentQuestionIndex = 0;
    const userResponses = {};

    const startQuiz = () => {
        welcomeScreen.classList.add('hidden');
        quizContainer.classList.remove('hidden');
        currentQuestionIndex = 0;
        // Limpiar respuestas anteriores para un nuevo intento
        for (const key in userResponses) {
            delete userResponses[key];
        }
        questionContainers.forEach((container, index) => {
            if (index === 0) {
                container.classList.remove('hidden');
            } else {
                container.classList.add('hidden');
            }
        });
    };

    const resetQuiz = () => {
        resultDiv.classList.add('hidden');
        quizContainer.classList.add('hidden');
        welcomeScreen.classList.remove('hidden');
    };
    
    startButton.addEventListener('click', startQuiz);

    const allOptionButtons = document.querySelectorAll('.option-button');
    allOptionButtons.forEach(button => {
        button.addEventListener('click', () => {
            const questionType = button.dataset.question;
            const answer = button.dataset.answer;
            
            if (questionType) {
                userResponses[questionType] = answer;
                
                questionContainers[currentQuestionIndex].classList.add('hidden');
                currentQuestionIndex++;
                
                if (currentQuestionIndex < questionContainers.length) {
                    questionContainers[currentQuestionIndex].classList.remove('hidden');
                } else {
                    sendDataToBackend();
                }
            }
        });
    });

    const sendDataToBackend = async () => {
        quizContainer.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        
        const formattedResponses = {
            tipo_producto_general: userResponses.tipo_producto_general,
            tipo_antojo: userResponses.tipo_antojo,
            base: userResponses.base,
            tipo_sabor: userResponses.tipo_sabor
        };

        try {
            // CORRECCIÓN CLAVE: Usar la ruta relativa '/recommend' en lugar de la URL completa.
            // Esto resuelve el "Error de Conexión: No se pudo contactar al servidor."
            const response = await fetch('/recommend', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formattedResponses),
            });

            if (!response.ok) {
                // Capturar el error del backend (Flask) si es un 400 o 500
                const errorData = await response.json();
                displayError(errorData.error || `Error del servidor: Código ${response.status}`);
                return;
            }

            const data = await response.json();
            displayRecommendation(data.recommended_product, data.weather);

        } catch (error) {
            console.error('Error de conexión:', error);
            displayError('Error de Conexión: No se pudo contactar al servidor. Asegúrate de que Flask esté corriendo.');
        } finally {
            loadingDiv.classList.add('hidden');
        }
    };

    const displayRecommendation = (product, weather) => {
        const weatherEmojis = {
            'soleado': '☀️',
            'nublado': '☁️',
            'lluvioso': '🌧️'
        };
        const weatherEmoji = weatherEmojis[weather] || '🌡️';

        resultDiv.innerHTML = `
            <div class="recommendation-header">
                <h2>¡Tu recomendacion del dia es!</h2>
                <p class="weather-info">El clima es ${weather} ${weatherEmoji}</p>
            </div>
            <div class="recommendation-card">
                <h3>${product.name}</h3>
                <p>Precio: ${product.price}</p>
                <img src="/static/images/${product.image}" alt="${product.name}" class="product-image">
                <p class="justification">${product.justification}</p>
            </div>
            <button id="restart-button" class="option-button">Regresar</button>
        `;
        resultDiv.classList.remove('hidden');
        
        document.getElementById('restart-button').addEventListener('click', resetQuiz);
    };

    // FUNCIÓN AGREGADA para manejar y mostrar los errores de forma coherente
    const displayError = (message) => {
        resultDiv.innerHTML = `
            <div class="recommendation-header">
                <h2>¡UPS!</h2>
                <p class="weather-info">${message}</p>
            </div>
            <button id="restart-button" class="option-button">Regresar</button>
        `;
        resultDiv.classList.remove('hidden');
        loadingDiv.classList.add('hidden');
        document.getElementById('restart-button').addEventListener('click', resetQuiz);
    }
});