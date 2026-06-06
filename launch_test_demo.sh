#!/bin/bash
# Launch demo of enhanced GUI features

echo "🚀 Launching Enhanced GUI Demo..."
echo "This demonstrates the new expandable rows and filtering features"
echo ""

# Check if we have a display
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    echo "❌ No display available - this demo requires GUI"
    exit 1
fi

# Run the simple demo (no dependencies needed)
python3 test_gui_simple.py