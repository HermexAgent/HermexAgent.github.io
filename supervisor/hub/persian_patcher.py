"""
HermexAgent Persian RTL & Vazirmatn Font 1-Click Patcher for Hermes WebUI
"""

import os
import re
import logging
import subprocess
from typing import Dict, Any

logger = logging.getLogger("HermexAgent.PersianPatcher")

VAZIRMATN_CDN_CSS = """
/* --- HermexAgent Persian RTL & Vazirmatn Font Patch --- */
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');

:root {
  --font-vazir: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body, button, input, select, textarea, .font-sans {
  font-family: var(--font-vazir) !important;
}

/* Smart RTL detection & styling for Persian/Arabic text */
[dir="rtl"], .rtl, .persian-text, :lang(fa), :lang(ar) {
  direction: rtl !important;
  text-align: right !important;
  font-family: var(--font-vazir) !important;
}

/* Auto RTL for Persian markdown & paragraphs */
p, li, h1, h2, h3, h4, h5, h6, .prose {
  unicode-bidi: plaintext !important;
  text-align: start !important;
}

/* Keep code blocks strictly LTR */
pre, code, kbd, samp, .font-mono, [class*="language-"] {
  direction: ltr !important;
  text-align: left !important;
  font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
  unicode-bidi: isolate !important;
}
"""

class PersianPatcher:
    @staticmethod
    def find_webui_directory() -> str:
        """Locate Hermes WebUI installation path."""
        possible_paths = [
            os.path.expanduser("~/.hermes/webui"),
            os.path.expanduser("~/.hermes-webui"),
            os.path.expanduser("~/workspace/hermes-webui"),
            os.path.expanduser("~/hermes-webui"),
            "/usr/local/share/hermes-webui"
        ]
        for p in possible_paths:
            if os.path.isdir(p):
                return p
        return ""

    @classmethod
    def apply_persian_rtl_patch(cls, custom_webui_path: str = "") -> Dict[str, Any]:
        """Inject Vazirmatn font & Smart RTL rules into Hermes WebUI CSS / HTML."""
        target_dir = custom_webui_path or cls.find_webui_directory()
        if not target_dir or not os.path.exists(target_dir):
            return {
                "success": False,
                "message": "Hermes WebUI directory not found. Please install Hermes WebUI first."
            }

        patched_files = []
        try:
            # Look for main CSS files (globals.css, index.css, style.css, App.css)
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".css") and any(name in file.lower() for name in ["global", "index", "style", "app", "main"]):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        if "HermexAgent Persian RTL" not in content:
                            with open(file_path, "a", encoding="utf-8") as f:
                                f.write("\n" + VAZIRMATN_CDN_CSS + "\n")
                            patched_files.append(file_path)

            if patched_files:
                return {
                    "success": True,
                    "message": f"Successfully injected Vazirmatn font and smart RTL into {len(patched_files)} stylesheet(s).",
                    "files": patched_files
                }
            else:
                return {
                    "success": True,
                    "message": "Stylesheets already patched with Vazirmatn font and RTL support."
                }
        except Exception as e:
            logger.error(f"Error applying Persian RTL patch: {e}")
            return {"success": False, "message": str(e)}
