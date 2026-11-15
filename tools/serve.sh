#!/bin/sh
# Local preview: http://localhost:8765
cd "$(dirname "$0")/../docs" && exec python3 -m http.server 8765
