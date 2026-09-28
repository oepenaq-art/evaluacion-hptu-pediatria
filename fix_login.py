import re

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Update handleLogin to normalize email
login_old = """async function handleLogin() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;"""

login_new = """async function handleLogin() {
    const email = document.getElementById('login-email').value.trim().toLowerCase();
    const password = document.getElementById('login-password').value;"""

js = js.replace(login_old, login_new)

# 2. Add Persistence explicit
init_old = """firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const functions = firebase.functions();"""

init_new = """firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const functions = firebase.functions();

// Forzar persistencia local para navegadores mviles restrictivos
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(e => console.error("Persistence error:", e));"""
init_new = init_new.replace("mviles", "móviles")

if 'auth.setPersistence' not in js:
    js = js.replace(init_old, init_new)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("app.js updated with login fixes.")
