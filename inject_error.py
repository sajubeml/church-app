import os

with open('index_supabase.html', 'r', encoding='utf-8') as f:
    html = f.read()

error_script = """
<script>
window.onerror = function(msg, url, line, col, error) {
  alert("Error: " + msg + "\\nLine: " + line);
};
window.addEventListener("unhandledrejection", function(e) {
  alert("Unhandled Rejection: " + (e.reason && e.reason.message ? e.reason.message : e.reason));
});
</script>
"""

if 'window.onerror' not in html:
    html = html.replace('<head>', '<head>' + error_script)
    with open('index_supabase.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('Injected error reporter.')
else:
    print('Already injected.')
