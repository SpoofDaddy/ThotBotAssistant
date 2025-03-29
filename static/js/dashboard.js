// Dashboard.js for Cherry Discord Bot

document.addEventListener('DOMContentLoaded', function() {
    // Check bot status periodically
    checkBotStatus();
    setInterval(checkBotStatus, 30000); // Check every 30 seconds
    
    // Initialize mood selector
    initMoodSelector();
    
    // Initialize refresh of top simps
    refreshTopSimps();
    setInterval(refreshTopSimps, 60000); // Refresh every minute
});

// Bot Status Check
function checkBotStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('bot-status');
            if (data.status === 'online') {
                statusElement.className = 'status-indicator online';
                statusElement.innerHTML = '<span class="pulse"></span> Bot Status: Online';
            } else {
                statusElement.className = 'status-indicator offline';
                statusElement.innerHTML = '<span class="pulse"></span> Bot Status: Offline';
            }
        })
        .catch(error => {
            console.error('Error checking bot status:', error);
            document.getElementById('bot-status').className = 'status-indicator offline';
            document.getElementById('bot-status').innerHTML = '<span class="pulse"></span> Bot Status: Error';
        });
}

// Top Simps Refresh
function refreshTopSimps() {
    fetch('/api/top_simps')
        .then(response => response.json())
        .then(data => {
            const leaderboardContainer = document.getElementById('leaderboard-items');
            if (!leaderboardContainer) return;
            
            if (data.top_simps && data.top_simps.length > 0) {
                let html = '';
                data.top_simps.forEach((simp, index) => {
                    html += `
                    <div class="leaderboard-item">
                        <div class="rank">#${index + 1}</div>
                        <div class="user">User ${simp.user_id}</div>
                        <div class="score">${simp.score}</div>
                    </div>`;
                });
                leaderboardContainer.innerHTML = html;
            } else {
                leaderboardContainer.innerHTML = '<div class="leaderboard-item text-center">No simps yet!</div>';
            }
        })
        .catch(error => {
            console.error('Error refreshing top simps:', error);
        });
}

// Mood Selector Functionality
function initMoodSelector() {
    const moodButtons = document.querySelectorAll('.mood-button');
    
    moodButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            moodButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            const mood = this.getAttribute('data-mood');
            
            // In the future, this would send the selected mood to an API
            console.log('Selected mood:', mood);
            
            // Show toast notification
            showToast(`Personality set to: ${mood} mode!`);
            
            // Update personality description
            updatePersonalityDescription(mood);
        });
    });
}

// Update personality description based on selected mood
function updatePersonalityDescription(mood) {
    const descriptionElement = document.getElementById('personality-description');
    if (!descriptionElement) return;
    
    let description = '';
    switch(mood) {
        case 'default':
            description = 'Flirty, playful, and fun! Cherry loves complimenting users and making everyone feel special.';
            break;
        case 'tsundere':
            description = '"I-It\'s not like I like you or anything, b-baka!" Cherry pretends to be cold but secretly has a sweet side.';
            break;
        case 'wholesome':
            description = 'Sweet as sugar! Cherry is extra supportive, wholesome, and heartwarming with every response.';
            break;
        case 'spicy':
            description = 'Extra flirty and a little bit naughty. Cherry cranks up the sass and spice for more mature servers.';
            break;
        case 'yandere':
            description = 'Obsessive and intense! Cherry is extremely attached to users and might get a little... possessive.';
            break;
        default:
            description = 'Flirty, playful, and fun! Cherry loves complimenting users and making everyone feel special.';
    }
    
    descriptionElement.textContent = description;
}

// Toast Notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Trigger reflow to ensure transition works
    toast.offsetHeight;
    
    // Show toast
    toast.classList.add('show');
    
    // Hide and remove after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}