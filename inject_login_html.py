import re

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject CSS before </head>
css = """
  <style>
    /* Login Overlay Styles */
    #login-overlay {
      position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      display: flex; align-items: center; justify-content: center;
      z-index: 999999; font-family: 'Inter', sans-serif;
    }
    .login-card {
      background: rgba(255, 255, 255, 0.05);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      padding: 2.5rem; width: 90%; max-width: 400px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      text-align: center; color: white;
    }
    .login-card img { width: 80px; margin-bottom: 1rem; }
    .login-card h2 { margin: 0 0 1.5rem; font-size: 1.5rem; font-weight: 600; }
    .login-input {
      width: 100%; padding: 0.75rem 1rem; margin-bottom: 1rem;
      background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px; color: white; font-size: 1rem; outline: none;
      box-sizing: border-box; transition: border-color 0.2s;
    }
    .login-input:focus { border-color: #3b82f6; }
    .login-btn {
      width: 100%; padding: 0.75rem; background: #3b82f6;
      color: white; border: none; border-radius: 8px; font-size: 1rem;
      font-weight: 600; cursor: pointer; transition: background 0.2s;
    }
    .login-btn:hover { background: #2563eb; }
    .login-btn:disabled { background: #64748b; cursor: not-allowed; }
    #login-error { color: #ef4444; margin-top: 1rem; font-size: 0.875rem; display: none; }
  </style>
"""
if '<style>' not in html:
    html = html.replace('</head>', css + '</head>')

# 2. Inject HTML after <body> and wrap the rest in main-app-container
overlay_html = """
<div id="login-overlay">
  <div class="login-card">
    <img src="church_logo.png" alt="Logo">
    <h2>Secure Gateway</h2>
    <input type="email" id="login-email" class="login-input" placeholder="Email Address" required>
    <input type="password" id="login-password" class="login-input" placeholder="Password" required>
    <button id="login-submit" class="login-btn" onclick="attemptLogin()">Login</button>
    <div id="login-error"></div>
  </div>
</div>
<div id="main-app-container" style="display: none;">
"""

if '<div id="login-overlay">' not in html:
    html = html.replace('<body>', '<body>\n' + overlay_html)
    # close the div at the very end before </body>
    html = html.replace('</body>', '\n</div>\n</body>')

with open('index_supabase.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated HTML.")
