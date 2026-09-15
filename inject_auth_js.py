import re

with open("app_supabase.js", "r", encoding="utf-8") as f:
    js = f.read()

# Replace the Authorization header everywhere inside the fetch interceptor
js = js.replace("'Authorization': 'Bearer ' + SUPABASE_ANON_KEY", "'Authorization': window.SUPABASE_ACCESS_TOKEN ? 'Bearer ' + window.SUPABASE_ACCESS_TOKEN : 'Bearer ' + SUPABASE_ANON_KEY")

# Add the attemptLogin function at the top
LOGIN_FUNC = """
window.SUPABASE_ACCESS_TOKEN = null;

window.attemptLogin = async function() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    const btn = document.getElementById('login-submit');
    
    if (!email || !password) {
        errorDiv.textContent = "Please enter email and password.";
        errorDiv.style.display = "block";
        return;
    }
    
    btn.disabled = true;
    btn.textContent = "Authenticating...";
    errorDiv.style.display = "none";
    
    try {
        const res = await originalFetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
            method: 'POST',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email: email, password: password })
        });
        
        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.error_description || data.msg || "Authentication failed");
        }
        
        // Success! Save token
        window.SUPABASE_ACCESS_TOKEN = data.access_token;
        
        // Hide overlay and show app
        document.getElementById('login-overlay').style.display = 'none';
        document.getElementById('main-app-container').style.display = 'block';
        
        // Trigger data reload now that we have the secure token!
        if (typeof loadAllData === 'function') {
            loadAllData();
        }
        
    } catch(err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = "block";
        btn.disabled = false;
        btn.textContent = "Login";
    }
};

"""

if "window.attemptLogin" not in js:
    js = js.replace("const originalFetch = window.fetch;", LOGIN_FUNC + "\nconst originalFetch = window.fetch;")

with open("app_supabase.js", "w", encoding="utf-8") as f:
    f.write(js)
print("Injected login logic into app_supabase.js")

# Update cache buster
with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()
html = re.sub(r'app_supabase\.js\?v=\d+', 'app_supabase.js?v=9999', html)
with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated cache buster.")
