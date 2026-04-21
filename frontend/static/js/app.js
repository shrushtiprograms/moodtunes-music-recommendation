let currentEmotion = null;
let currentSongs = [];
let selectedCategory = 'All';
let selectedSort = 'default';
let lastInput = '';
let lastConfidence = 0;
// kajal 
function isEmptyInput(text) {
    return text.trim().length === 0;
}

// Only numbers
function isOnlyNumbers(text) {
    return /^[0-9]+$/.test(text);
}

// Only special characters (but NOT spaces)
function isOnlySpecialChars(text) {
    return /^[^A-Za-z0-9\s]+$/.test(text);
}

// Contains numbers + letters mixed
function isMixedWithNumbers(text) {
    return /[0-9]/.test(text) && /[A-Za-z]/.test(text);
}

// Contains symbols + letters mixed (IGNORE spaces)
function isMixedWithSymbols(text) {
    return /[^A-Za-z0-9\s]/.test(text) && /[A-Za-z]/.test(text);
}

// Everything mixed (numbers + symbols + letters)
function isFullyMixed(text) {
    return /[0-9]/.test(text) &&
           /[^A-Za-z0-9\s]/.test(text) &&
           /[A-Za-z]/.test(text);
}
function isNumbersAndSymbols(text) {
    return /[0-9]/.test(text) && /[^A-Za-z0-9\s]/.test(text) && !/[A-Za-z]/.test(text);
}


// 

document.addEventListener('DOMContentLoaded', function() {
    initializeSettingsPanel();
    setupEnterKeyListener();
    loadSettingsFromStorage();
});

function initializeSettingsPanel() {
    const settingsBtn = document.getElementById('settingsBtn');
    const settingsPanel = document.getElementById('settingsPanel');
    const closeSettings = document.getElementById('closeSettings');
    const panelOverlay = document.getElementById('panelOverlay');
    const colorOptions = document.querySelectorAll('.color-option');
    const darkModeToggle = document.getElementById('darkModeToggle');

    // Open settings panel
    settingsBtn.addEventListener('click', function() {
        settingsPanel.classList.add('open');
        panelOverlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    });

    // Close settings panel
    closeSettings.addEventListener('click', closeSettingsPanel);
    panelOverlay.addEventListener('click', closeSettingsPanel);

    // Color selection
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            const theme = this.dataset.theme;
            
            // Update active state
            colorOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            
            // Preview theme change
            changeColorTheme(theme);
        });
    });

    // Dark mode toggle
    darkModeToggle.addEventListener('change', function() {
        toggleDarkMode(this.checked);
    });

    // Set initial filter values
    document.querySelector('input[name="category"][value="All"]').checked = true;
    document.querySelector('input[name="sort"][value="default"]').checked = true;
}

function closeSettingsPanel() {
    const settingsPanel = document.getElementById('settingsPanel');
    const panelOverlay = document.getElementById('panelOverlay');
    
    settingsPanel.classList.remove('open');
    panelOverlay.classList.remove('show');
    document.body.style.overflow = '';
    
    // Revert to saved theme if changes weren't applied
    loadSettingsFromStorage();
}

function setupEnterKeyListener() {
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeMood();
        }
    });
}

function changeColorTheme(theme) {
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${theme}`);
}

function toggleDarkMode(enabled) {
    if (enabled) {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
}

function applySettings() {
    // Get selected values
    selectedCategory = document.querySelector('input[name="category"]:checked').value;
    selectedSort = document.querySelector('input[name="sort"]:checked').value;
    
    // Get current theme from active color option
    const activeTheme = document.querySelector('.color-option.active').dataset.theme;
    const darkModeEnabled = document.getElementById('darkModeToggle').checked;
    
    // Save to localStorage
    localStorage.setItem('colorTheme', activeTheme);
    localStorage.setItem('darkMode', darkModeEnabled ? 'enabled' : 'disabled');
    localStorage.setItem('selectedCategory', selectedCategory);
    localStorage.setItem('selectedSort', selectedSort);
    
    // Apply settings
    changeColorTheme(activeTheme);
    toggleDarkMode(darkModeEnabled);
    
    // Close panel
    closeSettingsPanel();
    
    // Refresh recommendations if we have current emotion
    if (currentEmotion && lastInput) {
        fetchRecommendations();
    }
    
    showNotification('Settings applied successfully!');
}

function resetSettings() {
    // Reset to default values
    document.querySelector('input[name="category"][value="All"]').checked = true;
    document.querySelector('input[name="sort"][value="default"]').checked = true;
    document.querySelector('.color-option[data-theme="purple"]').classList.add('active');
    document.getElementById('darkModeToggle').checked = false;
    
    // Remove other active classes
    document.querySelectorAll('.color-option').forEach(opt => {
        if (opt.dataset.theme !== 'purple') {
            opt.classList.remove('active');
        }
    });
    
    // Preview changes
    changeColorTheme('purple');
    toggleDarkMode(false);
    
    showNotification('Settings reset to default!');
}

function loadSettingsFromStorage() {
    const savedTheme = localStorage.getItem('colorTheme') || 'purple';
    const savedMode = localStorage.getItem('darkMode') === 'enabled';
    const savedCategory = localStorage.getItem('selectedCategory') || 'All';
    const savedSort = localStorage.getItem('selectedSort') || 'default';
    
    // Apply settings
    changeColorTheme(savedTheme);
    toggleDarkMode(savedMode);
    
    // Update UI elements
    document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('active'));
    document.querySelector(`.color-option[data-theme="${savedTheme}"]`).classList.add('active');
    document.getElementById('darkModeToggle').checked = savedMode;
    
    // Update filter selections
    document.querySelector(`input[name="category"][value="${savedCategory}"]`).checked = true;
    document.querySelector(`input[name="sort"][value="${savedSort}"]`).checked = true;
    
    selectedCategory = savedCategory;
    selectedSort = savedSort;
}

function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1002;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS for notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

async function analyzeMood() {
    const input = document.getElementById('searchInput').value.trim();
    const resultsContainer = document.getElementById('resultsContainer');
    // ⭐⭐ PASTE THIS BLOCK HERE ⭐⭐
    // 1️⃣ No input at all
// 1️⃣ Empty input
    // 1️⃣ Empty input
    if (isEmptyInput(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                🎵 Tell me how you're feeling… don’t leave it blank!
            </div>
        </div>
    `;
    return;
    }

// 2️⃣ Fully mixed (letters + numbers + symbols)
    if (isFullyMixed(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                🌀 This looks like a password 😆<br>
                Tell me your mood in simple words!
            </div>
        </div>
    `;
    return;
    }

// 3️⃣ Letters + numbers mixed (NO symbols)
    if (isMixedWithNumbers(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                🔤➕🔢 Mixed input detected!<br>
                Use words only to describe your mood.
            </div>
        </div>
    `;
    return;
    }

// 4️⃣ Letters + symbols mixed (NO numbers)
    if (isMixedWithSymbols(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                ✨ Words + symbols confuse me 😅<br>
                Try writing your mood clearly!
            </div>
        </div>
    `;
    return;
    }

// 5️⃣ Only numbers
    if (isOnlyNumbers(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                🔢 Numbers can't express emotions!
            </div>
        </div>
    `;
    return;
    }
    // 5.1️⃣ Numbers + Symbols (NO letters)
    if (isNumbersAndSymbols(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                🔢➕✨ Numbers + symbols can't express emotions!  
                Try using simple mood words.
            </div>
        </div>`;
    return;
    }


// 6️⃣ Only symbols
    if (isOnlySpecialChars(input)) {
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-text" style="color: var(--danger);">
                ✨ Symbols don't have feelings 😅<br>
                Use words to describe your mood!
            </div>
        </div>
    `;
    return;
    }

    // ⭐⭐ END OF BLOCK ⭐⭐

    if (!input) {
        resultsContainer.innerHTML = `
            <div class="search-card glass-effect">
                <div class="loading-text" style="color: var(--danger);">
                    ⚠️ Please enter your mood or feeling
                </div>
            </div>
        `;
        return;
    }
    
    lastInput = input;
    
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-wrapper">
                <div class="loading-spinner"></div>
                <div class="loading-text">Analyzing your mood and finding perfect songs...</div>
            </div>
        </div>
    `;
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: input,
                category: selectedCategory,
                sort: selectedSort
            }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        currentEmotion = data.emotion;
        currentSongs = data.recommendations || [];
        lastConfidence = data.confidence;
        
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        resultsContainer.innerHTML = `
            <div class="search-card glass-effect">
                <div class="loading-text" style="color: var(--danger);">
                    ❌ Error: ${error.message}
                </div>
            </div>
        `;
    }
}

async function fetchRecommendations() {
    const resultsContainer = document.getElementById('resultsContainer');
    
    resultsContainer.innerHTML = `
        <div class="search-card glass-effect">
            <div class="loading-wrapper">
                <div class="loading-spinner"></div>
                <div class="loading-text">Updating recommendations...</div>
            </div>
        </div>
    `;
    
    try {
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                emotion: currentEmotion,
                category: selectedCategory,
                limit: 10
            }),
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        let songs = data.songs || [];
        
        if (selectedSort === 'asc') {
            songs.sort((a, b) => a.title.localeCompare(b.title));
        } else if (selectedSort === 'desc') {
            songs.sort((a, b) => b.title.localeCompare(a.title));
        }
        
        currentSongs = songs;
        
        displayResults({
            emotion: currentEmotion,
            recommendations: currentSongs,
            confidence: lastConfidence
        });
        
    } catch (error) {
        console.error('Error:', error);
        resultsContainer.innerHTML = `
            <div class="search-card glass-effect">
                <div class="loading-text" style="color: var(--danger);">
                    ❌ Error: ${error.message}
                </div>
            </div>
        `;
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    const { emotion, recommendations } = data;
    
    const emotionEmoji = getEmotionEmoji(emotion);
    
    let html = `
        <div class="emotion-badge">
            <span>${emotionEmoji}</span>
            <span>${emotion}</span>
        </div>
    `;
    
    if (recommendations && recommendations.length > 0) {
        html += '<div class="song-grid">';
        
        recommendations.forEach(song => {
            // Extract YouTube ID from youtube_link if available
            let youtubeId = "N/A";
            if (song.youtube_id && song.youtube_id !== "N/A") {
                youtubeId = song.youtube_id;
            } else if (song.youtube_link && song.youtube_link !== "N/A") {
                // Extract ID from full YouTube URL
                const youtubeMatch = song.youtube_link.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
                if (youtubeMatch) {
                    youtubeId = youtubeMatch[1];
                }
            }
            
            // Create Spotify embed URL from spotify_link if available
            let spotifyEmbed = "N/A";
            if (song.spotify_embed && song.spotify_embed !== "N/A") {
                spotifyEmbed = song.spotify_embed;
            } else if (song.spotify_link && song.spotify_link !== "N/A") {
                // Convert Spotify track URL to embed URL
                const spotifyMatch = song.spotify_link.match(/spotify\.com\/track\/([a-zA-Z0-9]+)/);
                if (spotifyMatch) {
                    spotifyEmbed = `https://open.spotify.com/embed/track/${spotifyMatch[1]}?utm_source=generator`;
                }
            }
            
            const hasYoutube = youtubeId !== "N/A";
            const hasSpotify = spotifyEmbed !== "N/A";
            
            html += `
                <div class="song-card glass-effect">
                    <div class="song-header">
                        <div class="song-title">${escapeHtml(song.title)}</div>
                        <div class="song-artist">🎤 ${escapeHtml(song.artist)}</div>
                    </div>
                    
                    <div class="song-meta">
                        <span class="tag tag-emotion">${song.emotion}</span>
                        <span class="tag tag-category">${song.category}</span>
                    </div>
                    
                    <div class="song-players">
                        <div class="players-grid">
            `;
            
            if (hasYoutube) {
                html += `
                    <div class="player-container youtube-player">
                        <iframe 
                            src="https://www.youtube.com/embed/${youtubeId}"
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                    </div>
                `;
            } else {
                html += `
                    <div class="player-container youtube-player">
                        <div class="no-player-message">
                            <div>📹 YouTube video not available</div>
                            ${song.youtube_link && song.youtube_link !== "N/A" ? 
                                `<a href="${song.youtube_link}" target="_blank" style="color: var(--primary); margin-top: 5px; display: block;">Open in YouTube</a>` : 
                                ''
                            }
                        </div>
                    </div>
                `;
            }
            
            if (hasSpotify) {
                html += `
                    <div class="player-container spotify-player">
                        <iframe 
                            src="${spotifyEmbed}"
                            frameborder="0"
                            allowtransparency="true"
                            allow="encrypted-media">
                        </iframe>
                    </div>
                `;
            } else {
                html += `
                    <div class="player-container spotify-player">
                        <div class="no-player-message">
                            <div>🎵 Spotify preview not available</div>
                            ${song.spotify_link && song.spotify_link !== "N/A" ? 
                                `<a href="${song.spotify_link}" target="_blank" style="color: var(--primary); margin-top: 5px; display: block;">Open in Spotify</a>` : 
                                ''
                            }
                        </div>
                    </div>
                `;
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    } else {
        html += `
            <div class="search-card glass-effect">
                <div class="loading-text">
                    😔 No songs found for this mood. Try a different description!
                </div>
            </div>
        `;
    }
    
    resultsContainer.innerHTML = html;
}

function getEmotionEmoji(emotion) {
    const emojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'love': '❤️',
        'excited': '🎉',
        'calm': '😌',
        'anxious': '😰',
        'frustrated': '😤',
        'neutral': '😐',
        'sleepy': '😴',
        'hungry': '🍔',
        'thirsty': '🥤',
        'sick': '🤒',
        'bored': '😑',
        'surprised': '😲',
        'confused': '😵',
        'proud': '😊',
        'jealous': '😒',
        'nostalgic': '🎞️',
        'hopeful': '🌈',
        'blessed': '😇',
        'disgusted': '🤢',
        'dizzy': '😵',
        'hot': '🔥',
        'cold': '❄️',
        'mischievous': '😈',
        'playful': '😄',
        'focused': '🎯',
        'loving': '🫶',
        'friendly': '🤝'
    };
    return emojis[emotion.toLowerCase()] || '🎵';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}