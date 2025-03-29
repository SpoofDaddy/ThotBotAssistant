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
    
    // Initialize welcome messages toggle
    initWelcomeMessagesToggle();
    
    // Get current personality
    fetch('/api/personality')
        .then(response => response.json())
        .then(data => {
            if (data.current_personality) {
                // Find the mood button for this personality and set it as active
                const buttons = document.querySelectorAll('.mood-button');
                buttons.forEach(button => {
                    if (button.getAttribute('data-mood') === data.current_personality) {
                        button.classList.add('active');
                    } else {
                        button.classList.remove('active');
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error fetching current personality:', error);
        });
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
            const mood = this.getAttribute('data-mood');
            const moodName = this.textContent.trim();
            
            // Don't do anything if already active
            if (this.classList.contains('active')) return;
            
            // Set the personality via API
            setPersonality(mood, moodName, this);
        });
    });
}

// Set personality via API call
function setPersonality(personality, personalityName, buttonElement) {
    // Show loading state
    const originalText = buttonElement.textContent;
    buttonElement.textContent = "Setting...";
    buttonElement.style.opacity = "0.7";
    
    fetch('/api/personality', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            personality: personality
        })
    })
    .then(response => response.json())
    .then(data => {
        // Reset button state
        buttonElement.textContent = originalText;
        buttonElement.style.opacity = "1";
        
        if (data.success) {
            // Remove active class from all buttons
            document.querySelectorAll('.mood-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to this button
            buttonElement.classList.add('active');
            
            // Show success toast notification
            showToast(`Personality set to: ${personalityName} mode!`, 'success');
            
            // Update personality description
            updatePersonalityDescription(personality, buttonElement);
        } else {
            // Show error toast
            showToast(`Error: ${data.message || 'Failed to change personality'}`, 'error');
        }
    })
    .catch(error => {
        // Reset button state
        buttonElement.textContent = originalText;
        buttonElement.style.opacity = "1";
        
        console.error('Error setting personality:', error);
        showToast('Error: Failed to set personality. Please try again.', 'error');
    });
}

// Update personality description based on selected mood
function updatePersonalityDescription(mood, buttonElement) {
    const descriptionElement = document.getElementById('personality-description');
    if (!descriptionElement) return;
    
    // Get description from button's data attribute
    const description = buttonElement.getAttribute('data-description');
    if (description) {
        descriptionElement.textContent = description;
    }
}

// Welcome Messages Toggle Functionality
function initWelcomeMessagesToggle() {
    const welcomeToggle = document.getElementById('welcome-messages-toggle');
    if (!welcomeToggle) return;
    
    // First, get current status from API
    fetch('/api/welcome_messages')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Set the toggle to match current state
                welcomeToggle.checked = data.enabled;
            }
        })
        .catch(error => {
            console.error('Error getting welcome messages status:', error);
        });
    
    // Add event listener for toggle changes
    welcomeToggle.addEventListener('change', function() {
        const isEnabled = this.checked;
        
        // Update via API
        fetch('/api/welcome_messages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                enabled: isEnabled
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast(`Welcome messages ${isEnabled ? 'enabled' : 'disabled'}`, 'success');
            } else {
                // If failed, revert the toggle and show error
                welcomeToggle.checked = !isEnabled;
                showToast(`Error: ${data.message || 'Failed to update welcome messages setting'}`, 'error');
            }
        })
        .catch(error => {
            // If error, revert the toggle
            welcomeToggle.checked = !isEnabled;
            console.error('Error updating welcome messages setting:', error);
            showToast('Error: Failed to update welcome messages setting', 'error');
        });
    });
}

// Toast Notification
function showToast(message, type = 'default') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    // Add appropriate class based on toast type
    if (type === 'success') {
        toast.classList.add('success');
    } else if (type === 'error') {
        toast.classList.add('error');
    } else if (type === 'warning') {
        toast.classList.add('warning');
    }
    
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