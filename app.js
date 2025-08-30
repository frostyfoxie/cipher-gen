// ------------------ Firebase Config ------------------
const firebaseConfig = {
  apiKey: "AIzaSyCqobhf4HFUdBIZJMF-s9uW3e0-EGh327I",
  authDomain: "anonymous-chatting-c6712.firebaseapp.com",
  databaseURL: "https://anonymous-chatting-c6712-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "anonymous-chatting-c6712",
  storageBucket: "anonymous-chatting-c6712.firebasestorage.app",
  messagingSenderId: "124331866043",
  appId: "1:124331866043:web:8be37be9d84974b4a0b69e",
  measurementId: "G-WVDHPRB41K"
};
firebase.initializeApp(firebaseConfig);
const db = firebase.database();
const storage = firebase.storage();

// ------------------ User Setup ------------------
let userId = localStorage.getItem('uid');
if (!userId) {
    userId = crypto.randomUUID();
    localStorage.setItem('uid', userId);
}

let userProfile = {
    nickname: '',
    avatar: 'https://i.pravatar.cc/40'
};

// ------------------ DOM Elements ------------------
const nicknameInput = document.getElementById('nickname');
const avatarPreview = document.getElementById('avatar-preview');
const avatarUpload = document.getElementById('avatar-upload');
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const imageBtn = document.getElementById('image-btn');
const imageInput = document.getElementById('image-input');

// ------------------ Load User Profile ------------------
function loadUserProfile() {
    db.ref('users/' + userId).once('value').then(snapshot => {
        if (snapshot.exists()) {
            userProfile = snapshot.val();
            nicknameInput.value = userProfile.nickname;
            avatarPreview.src = userProfile.avatar;
        } else {
            // Assign default nickname
            userProfile.nickname = `User${Math.floor(Math.random()*1000)}`;
            db.ref('users/' + userId).set(userProfile);
            nicknameInput.value = userProfile.nickname;
        }
    });
}
loadUserProfile();

// ------------------ Update Profile ------------------
nicknameInput.addEventListener('change', () => {
    userProfile.nickname = nicknameInput.value || `User${Math.floor(Math.random()*1000)}`;
    db.ref('users/' + userId).update({nickname: userProfile.nickname});
});

avatarUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const storageRef = storage.ref('avatars/' + userId);
    await storageRef.put(file);
    const url = await storageRef.getDownloadURL();
    avatarPreview.src = url;
    userProfile.avatar = url;
    db.ref('users/' + userId).update({avatar: url});
});

// ------------------ AES Encryption ------------------
async function getKey(password) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey('raw', enc.encode(password), {name:'PBKDF2'}, false, ['deriveKey']);
    return crypto.subtle.deriveKey({name:'PBKDF2', salt: enc.encode('salt1234'), iterations:100000, hash:'SHA-256'}, keyMaterial, {name:'AES-GCM', length:256}, false, ['encrypt','decrypt']);
}

async function encryptText(text, password) {
    const key = await getKey(password);
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const enc = new TextEncoder();
    const encrypted = await crypto.subtle.encrypt({name:'AES-GCM', iv}, key, enc.encode(text));
    const arr = new Uint8Array(iv.length + encrypted.byteLength);
    arr.set(iv, 0);
    arr.set(new Uint8Array(encrypted), iv.length);
    return btoa(String.fromCharCode(...arr));
}

async function decryptText(data, password) {
    const key = await getKey(password);
    const raw = Uint8Array.from(atob(data), c => c.charCodeAt(0));
    const iv = raw.slice(0,12);
    const encrypted = raw.slice(12);
    const decrypted = await crypto.subtle.decrypt({name:'AES-GCM', iv}, key, encrypted);
    return new TextDecoder().decode(decrypted);
}

// ------------------ Send Message ------------------
sendBtn.addEventListener('click', async () => {
    const text = messageInput.value.trim();
    if (!text) return;
    const encrypted = await encryptText(text, 'defaultkey'); // you can use session key
    const msgId = crypto.randomUUID();
    db.ref('messages/' + msgId).set({
        userId: userId,
        text: encrypted,
        image: null,
        timestamp: Date.now()
    });
    messageInput.value = '';
});

imageBtn.addEventListener('click', () => imageInput.click());

imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const storageRef = storage.ref('images/' + crypto.randomUUID() + '_' + file.name);
    await storageRef.put(file);
    const url = await storageRef.getDownloadURL();
    const encrypted = await encryptText(url, 'defaultkey');
    const msgId = crypto.randomUUID();
    db.ref('messages/' + msgId).set({
        userId: userId,
        text: null,
        image: encrypted,
        timestamp: Date.now()
    });
});

// ------------------ Display Messages ------------------
db.ref('messages').on('child_added', async (snapshot) => {
    const msg = snapshot.val();
    const senderSnapshot = await db.ref('users/' + msg.userId).once('value');
    const sender = senderSnapshot.val();
    const div = document.createElement('div');
    div.classList.add('message');
    div.dataset.msgId = snapshot.key;

    // Bubble HTML
    let content = `<img class="avatar" src="${sender.avatar}" title="${sender.nickname}">`;
    content += `<div class="bubble"><div class="meta"><span>${sender.nickname}</span><span>${new Date(msg.timestamp).toLocaleTimeString()}</span></div>`;

    if (msg.text) {
        const decrypted = await decryptText(msg.text, 'defaultkey');
        content += `<span>${decrypted}</span>`;
    }
    if (msg.image) {
        const decryptedURL = await decryptText(msg.image, 'defaultkey');
        content += `<img src="${decryptedURL}">`;
    }

    // Actions for edit/delete if this user
    if (msg.userId === userId) {
        content += `<div class="actions">
            <i class="fas fa-edit" onclick="editMessage('${snapshot.key}')"></i>
            <i class="fas fa-trash" onclick="deleteMessage('${snapshot.key}')"></i>
        </div>`;
    }

    content += `</div>`;
    div.innerHTML = content;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
});

// ------------------ Edit / Delete ------------------
window.editMessage = async (msgId) => {
    const newText = prompt('Edit your message:');
    if (!newText) return;
    const encrypted = await encryptText(newText, 'defaultkey');
    db.ref('messages/' + msgId).update({text: encrypted});
};

window.deleteMessage = (msgId) => {
    if (confirm('Delete this message?')) {
        db.ref('messages/' + msgId).remove();
    }
};

// Update chat on change / remove
db.ref('messages').on('child_changed', snapshot => {
    chatBox.innerHTML = '';
    db.ref('messages').once('value').then(() => {}); // triggers child_added for all
});
db.ref('messages').on('child_removed', snapshot => {
    const div = chatBox.querySelector(`[data-msg-id="${snapshot.key}"]`);
    if (div) div.remove();
});
