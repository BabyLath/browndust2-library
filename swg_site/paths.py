from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"          # YAML catalogs (source of truth for names, prices, seasons)
LIB = ROOT / "lib"                  # Markdown pages, styles, scripts, images you edit
GENERATED = ROOT / "generated-docs" # written by swg-build / swg-serve; never edit by hand
SITE = ROOT / "site"                # final HTML output
BASE_CONFIG = ROOT / "zensical.toml"
BUILD_CONFIG = ROOT / ".zensical.generated.toml"
