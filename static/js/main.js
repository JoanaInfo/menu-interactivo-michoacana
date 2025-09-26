document.addEventListener('DOMContentLoaded', () => {
    const welcomeScreen = document.getElementById('welcome-screen');
    const startButton = document.getElementById('start-button');
    const quizContainer = document.getElementById('quiz-container');
    const questionContainers = document.querySelectorAll('.question-container');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('recommendation-result');

    // --- Variables de control ---
    let currentQuestionIndex = 0;
    const userResponses = {};
    
    // Si tienes audio, obtén el elemento (Asumo que el id es 'background-audio')
    const backgroundAudio = document.getElementById('background-audio');

    // Función que inicia el cuestionario
    const startQuiz = () => {
        // ... (Tu lógica de inicio aquí)
        welcomeScreen.classList.add('hidden');
        quizContainer.classList.remove('hidden');
        currentQuestionIndex = 0;
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
        if (backgroundAudio) {
            backgroundAudio.play().catch(e => console.log("Audio play blocked:", e));
        }
    };

    const resetQuiz = () => {
        resultDiv.classList.add('hidden');
        quizContainer.classList.add('hidden');
        welcomeScreen.classList.remove('hidden');
        if (backgroundAudio) {
            backgroundAudio.pause();
            backgroundAudio.currentTime = 0;
        }
    };
    
    startButton.addEventListener('click', startQuiz);

    // Lógica para avanzar en las preguntas
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

    // --- FUNCIÓN CRÍTICA: ENVÍA Y RECIBE LA RECOMENDACIÓN ---
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
            const response = await fetch('https://menu-interactivo-michoacana.onrender.com/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formattedResponses),
            });
            
            // Si el servidor responde con un código de error (4xx o 5xx)
            if (!response.ok) {
                const errorData = await response.json();
                displayError(`Error ${response.status}: ${errorData.error || 'Fallo de la predicción.'}`);
                return;
            }

            // Si es exitoso (código 200)
            const data = await response.json();
            displayRecommendation(data.recommended_product, data.weather);

        } catch (error) {
            // Este bloque captura errores de red (Ej. servidor caído, timeout)
            displayError('Error de Conexión: No se pudo contactar al servidor. Reintenta.');
            console.error('Network Error:', error);
        } finally {
            loadingDiv.classList.add('hidden');
        }
    };

    // --- FUNCIONES DE DISPLAY ---
    const displayRecommendation = (product, weather) => {
        const weatherEmojis = {
            'soleado': '☀️',
            'nublado': '☁️',
            'lluvioso': '🌧️'
        };
        const weatherEmoji = weatherEmojis[weather] || '';

        resultDiv.innerHTML = `
            <div class="recommendation-header">
                <h2 class="recommendation-title">¡Tu recomendación del día es!</h2>
                <p class="weather-info">El clima es ${weather} ${weatherEmoji}</p>
            </div>
            <div class="recommendation-card">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price">Precio: ${product.price}</p>
                <img src="/static/images/${product.image}" alt="${product.name}" class="product-image">
                <p class="product-justification">${product.justification}</p>
            </div>
            <button id="restart-button" class="option-button">Regresar</button>
        `;
        resultDiv.classList.remove('hidden');
        
        document.getElementById('restart-button').addEventListener('click', resetQuiz);
    };

    const displayError = (message) => {
        // Aseguramos que el contenedor de resultados se muestre para que el usuario vea el error
        resultDiv.innerHTML = `
            <h2 style="color: red;">¡UPS! </h2>
            <p>${message}</p>
            <button id="restart-button" class="option-button">Regresar</button>
        `;
        resultDiv.classList.remove('hidden');
        document.getElementById('restart-button').addEventListener('click', resetQuiz);
    };
});