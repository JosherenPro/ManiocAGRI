import os
import re

PRELOADER_HTML = """
    <!-- Preloader -->
    <div id="preloader">
        <div class="loader-spinner"></div>
    </div>
"""

AOS_CSS = '    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">\n'
AOS_JS = """
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            AOS.init({
                duration: 800,
                once: true,
                offset: 50
            });
            // Hide preloader
            const preloader = document.getElementById('preloader');
            if (preloader) {
                setTimeout(() => {
                    preloader.classList.add('hidden');
                    setTimeout(() => preloader.remove(), 600);
                }, 500); // Small artificial delay for premium feel
            }
        });
    </script>
"""

def inject_aos_and_preloader(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # Inject AOS CSS before </head>
    if "aos.css" not in content and "</head>" in content:
        content = content.replace("</head>", AOS_CSS + "</head>")
        modified = True

    # Inject Preloader right after <body>
    if 'id="preloader"' not in content and "<body" in content:
        # Find exactly where body tag ends
        body_start = content.find("<body")
        body_end = content.find(">", body_start) + 1
        if body_start != -1:
            content = content[:body_end] + PRELOADER_HTML + content[body_end:]
            modified = True

    # Inject AOS JS before </body>
    if "aos.js" not in content and "</body>" in content:
        content = content.replace("</body>", AOS_JS + "</body>")
        modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Injected AOS and Preloader into {filepath}")
    else:
        print(f"Skipping {filepath} (Already injected)")

# Walk through frontend directory
frontend_dir = '/home/eren/Downloads/projet tutoré/projet tutoré/frontend'
for root, _, files in os.walk(frontend_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            inject_aos_and_preloader(filepath)

print("Insertion complete.")
