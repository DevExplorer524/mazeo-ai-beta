console.log("Mazeo AI Frontend Initialized. Welcome!");
document.addEventListener('DOMContentLoaded', () => {
    // Navigation Logic
    const navBtns = document.querySelectorAll('.nav-btn');
    const contentAreas = document.querySelectorAll('.content-area');
    const sectionTitle = document.getElementById('section-title');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update visible content area
            const mode = btn.dataset.mode;
            contentAreas.forEach(area => area.classList.remove('active'));

            if (mode === 'chat') {
                document.getElementById('chat-container').classList.add('active');
                sectionTitle.textContent = 'AI Chat';
            } else if (mode === 'search') {
                document.getElementById('search-container').classList.add('active');
                sectionTitle.textContent = 'Web Search';
            } else if (mode === 'image') {
                document.getElementById('image-container').classList.add('active');
                sectionTitle.textContent = 'Image Generation';
            }
        });
    });

    // Chat Logic
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const messagesContainer = document.getElementById('messages');
    const processingIndicator = document.getElementById('processing-indicator');
    const thinkingText = document.querySelector('.thinking-text');

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to UI
        appendMessage('user', message);
        userInput.value = '';

        // Show thinking indicator
        processingIndicator.classList.add('show');
        thinkingText.textContent = 'Thinking...';

        try {
            // Optional: simulate "thinking" step first
            const thinkRes = await fetch('/api/think', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: message })
            });
            const thinkData = await thinkRes.json();
            thinkingText.textContent = thinkData.thought; // Update thinking text

            // Get actual response
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            const data = await res.json();

            processingIndicator.classList.remove('show');
            appendMessage('system', data.response);

        } catch (error) {
            console.error('Error:', error);
            processingIndicator.classList.remove('show');
            appendMessage('system', 'Sorry, something went wrong.');
        }
    });

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'M';

        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        if (sender === 'system') {
            // Typing effect for AI
            let i = 0;
            const speed = 20; // ms per char

            function typeWriter() {
                if (i < text.length) {
                    bubble.textContent += text.charAt(i);
                    i++;

                    // Auto scroll while typing
                    const container = document.getElementById('chat-container');
                    container.scrollTop = container.scrollHeight;

                    setTimeout(typeWriter, speed);
                }
            }
            typeWriter();
        } else {
            bubble.textContent = text;
        }

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);

        messagesContainer.appendChild(msgDiv);

        // Scroll to bottom
        const container = document.getElementById('chat-container');
        container.scrollTop = container.scrollHeight;
    }

    // Search Logic
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (!query) return;

        searchResults.innerHTML = '<div class="loader" style="margin: 20px auto;"></div>';

        try {
            const res = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const data = await res.json();

            searchResults.innerHTML = '';
            if (data.results && data.results.length > 0) {
                data.results.forEach(result => {
                    const card = document.createElement('div');
                    card.className = 'result-card';
                    card.innerHTML = `
                        <h3><a href="${result.link}" style="color: inherit; text-decoration: none;">${result.title}</a></h3>
                        <p>${result.snippet}</p>
                    `;
                    searchResults.appendChild(card);
                });
            } else {
                searchResults.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No results found.</p>';
            }

        } catch (error) {
            searchResults.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Error searching.</p>';
        }
    });

    // Image Generation Logic
    const imageForm = document.getElementById('image-form');
    const imagePrompt = document.getElementById('image-prompt');
    const imageGallery = document.getElementById('image-gallery');

    imageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const prompt = imagePrompt.value.trim();
        const style = document.getElementById('image-style').value;
        if (!prompt) return;

        imageGallery.innerHTML = '<div class="loader" style="margin: 20px auto;"></div>';

        try {
            const res = await fetch('/api/generate_image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: prompt,
                    style: style
                })
            });
            const data = await res.json();

            imageGallery.innerHTML = '';
            const imgItem = document.createElement('div');
            imgItem.className = 'image-item';
            imgItem.innerHTML = `
                <img src="${data.image_url}" alt="${prompt}">
                <div class="image-caption">Generative AI: "${prompt}"</div>
            `;
            imageGallery.appendChild(imgItem);

        } catch (error) {
            imageGallery.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Error generating image.</p>';
        }
    });

    // Quick Image Preset Function
    window.quickImage = function (prompt, style) {
        const promptInput = document.getElementById('image-prompt');
        const styleSelect = document.getElementById('image-style');
        promptInput.value = prompt;
        styleSelect.value = style;
        imageForm.dispatchEvent(new Event('submit'));
    };

    // Make usePrompt available globally
    window.usePrompt = function (text) {
        const userInput = document.getElementById('user-input');
        userInput.value = text;
        userInput.focus();
    };

});
