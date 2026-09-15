import os

with open(r"c:\saju_old pc\Church_App\anti_gravity\app_cloud.js", "r", encoding="utf-8") as f:
    content = f.read()

error_handler = """
window.onerror = function(message, source, lineno, colno, error) {
    alert("CRITICAL ERROR in app_cloud.js:\\nLine: " + lineno + "\\nMessage: " + message);
    return false;
};
window.addEventListener('unhandledrejection', function(event) {
    alert("UNHANDLED PROMISE REJECTION:\\n" + event.reason);
});
"""

# Prepend it to the file
content = error_handler + content

with open(r"c:\saju_old pc\Church_App\anti_gravity\app_cloud.js", "w", encoding="utf-8") as f:
    f.write(content)

print("Injected global error handler into app_cloud.js")
