// Utility to show/hide sections
function showSection(sectionId) {
    document.getElementById('mainOptions').classList.add('hidden');
    document.getElementById('registerSection').classList.add('hidden');
    document.getElementById('authenticateSection').classList.add('hidden');
    document.getElementById(sectionId).classList.remove('hidden');
}
function showMainOptions() {
    document.getElementById('mainOptions').classList.remove('hidden');
    document.getElementById('registerSection').classList.add('hidden');
    document.getElementById('authenticateSection').classList.add('hidden');
    document.getElementById('userInfo').textContent = '';
    document.getElementById('result').textContent = '';
}

// Camera setup for both video elements
const video = document.getElementById('video');
const authVideo = document.getElementById('authVideo');
const canvas = document.getElementById('canvas');
const resultDiv = document.getElementById('result');
const userInfoDiv = document.getElementById('userInfo');

function startCamera(videoElement) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            videoElement.srcObject = stream;
        })
        .catch(err => {
            resultDiv.textContent = 'Camera access denied: ' + err.message;
        });
}

function captureImageBase64(videoElement) {
    canvas.getContext('2d').drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg').split(',')[1];
}

// Register logic
async function handleRegister(e) {
    e.preventDefault();
    resultDiv.textContent = '';
    userInfoDiv.textContent = '';
    const unique_id = document.getElementById('username').value;
    const name = document.getElementById('name').value;
    if (!unique_id || !name) {
        resultDiv.textContent = 'Please enter both username and name.';
        return;
    }
    const face_image = captureImageBase64(video);
    const payload = { unique_id, name, face_image };
    console.log('Register payload:', payload);
    try {
        const response = await fetch('http://localhost:8053/api/authentication/register/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        let data;
        try {
            data = await response.json();
        } catch (jsonErr) {
            throw new Error('Server error: Invalid response format.');
        }
        if (response.ok) {
            resultDiv.textContent = 'User registered successfully!';
            // Do not clear the message automatically
        } else if (data.unique_id && Array.isArray(data.unique_id) && data.unique_id[0].includes('already exists')) {
            resultDiv.textContent = 'A user with this username already exists. Please choose a different username.';
        } else {
            resultDiv.textContent = data.message || 'Registration failed.';
        }
    } catch (err) {
        resultDiv.textContent = 'Error: ' + err.message;
    }
}

// Authenticate logic
async function handleAuthenticate() {
    resultDiv.textContent = '';
    userInfoDiv.textContent = '';
    const face_image = captureImageBase64(authVideo);
    try {
        const response = await fetch('http://localhost:8053/api/authentication/authenticate/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ face_image })
        });
        const data = await response.json();
        if (response.ok && data.name) {
            userInfoDiv.textContent = `Authenticated User: ${data.name}`;
            resultDiv.textContent = 'Authentication successful!';
        } else if (response.ok && data.unique_id) {
            userInfoDiv.textContent = `Authenticated User ID: ${data.unique_id}`;
            resultDiv.textContent = 'Authentication successful!';
        } else if (response.ok && data.message) {
            userInfoDiv.textContent = '';
            resultDiv.textContent = data.message;
        } else {
            userInfoDiv.textContent = '';
            resultDiv.textContent = data.message || 'Authentication failed.';
        }
    } catch (err) {
        resultDiv.textContent = 'Error: ' + err.message;
        userInfoDiv.textContent = '';
    }
}

// UI event listeners
document.getElementById('showRegister').onclick = function() {
    showSection('registerSection');
    startCamera(video);
};
document.getElementById('showAuthenticate').onclick = function() {
    showSection('authenticateSection');
    startCamera(authVideo);
};
document.getElementById('backFromRegister').onclick = function() {
    showMainOptions();
    resultDiv.textContent = '';
    userInfoDiv.textContent = '';
};
document.getElementById('backFromAuth').onclick = showMainOptions;
document.getElementById('registerForm').onsubmit = handleRegister;
document.getElementById('authBtn').onclick = handleAuthenticate;

// Hide sections by default
showMainOptions(); 