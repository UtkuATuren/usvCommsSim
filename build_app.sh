#!/bin/bash

# UUV Communication Simulator - Build Script
# Creates a macOS .app bundle from the Python application

echo "🌊 Building UUV Communication Simulator.app..."

# Clean previous builds
echo "📁 Cleaning previous builds..."
rm -rf build/ dist/

# Build the app
echo "🔨 Building application bundle..."
python3 setup.py py2app

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Get app size
    APP_SIZE=$(du -sh "dist/UUV Communication Simulator.app" | cut -f1)
    echo "📊 App size: $APP_SIZE"
    
    # Create distribution info
    echo "📋 Creating distribution info..."
    cat > "dist/BUILD_INFO.txt" << EOF
🌊 UUV Communication Simulator - Build Information

Build Date: $(date)
App Size: $APP_SIZE
Python Version: $(python3 --version)
macOS Version: $(sw_vers -productVersion)
Architecture: Universal (x86_64 + arm64)

Files included:
- UUV Communication Simulator.app (main application)
- README_App.md (documentation)

Installation:
1. Move .app to Applications folder
2. Right-click and "Open" for first launch
3. Allow in Security & Privacy if needed

To distribute:
1. Compress the .app file
2. Include README_App.md
3. Test on different macOS versions
EOF

    # Copy README to dist
    cp README_App.md dist/
    
    echo "🎊 Build complete! Files in dist/ folder:"
    ls -la dist/
    
    echo ""
    echo "📱 To test the app:"
    echo "   open 'dist/UUV Communication Simulator.app'"
    echo ""
    echo "📦 To distribute:"
    echo "   1. Compress the .app file"
    echo "   2. Include README_App.md"
    echo "   3. Share the compressed file"
    
else
    echo "❌ Build failed!"
    exit 1
fi 