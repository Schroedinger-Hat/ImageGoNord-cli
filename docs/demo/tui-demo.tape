# ImageGoNord TUI demo
# Recorded with VHS: https://github.com/charmbracelet/vhs
#
# Types the input path, Escape to unfocus, cycles palettes, converts, shows help, quits.

Output docs/demo/tui-demo.gif

Set Theme "nord"
Set FontSize 14
Set Width 1200
Set Height 800
Set Padding 12

# Anonymise shell prompt and stage a demo image under /tmp
Type "export PS1='user@machine:~$ ' && clear"
Enter
Sleep 400ms

Type "mkdir -p /tmp/ign-demo && cp /tmp/demo-input.png /tmp/ign-demo/wallpaper.png && cd /tmp/ign-demo"
Enter
Sleep 300ms

# Launch TUI (starts with input-path field focused)
Type "ign tui"
Enter
Sleep 4500ms

# Type the input path directly into the focused input-path field
Type "/tmp/ign-demo/wallpaper.png"
Sleep 400ms
Escape
Sleep 600ms

# Cycle through a few palettes ([/] are priority — work even with Input focused)
Type "["
Sleep 700ms
Type "["
Sleep 700ms
Type "]"
Sleep 900ms

# Convert the image (c is priority — fires even with Input focused)
Type "c"
Sleep 4000ms

# Show the help overlay, then quit
Type "h"
Sleep 3000ms
Escape
Sleep 800ms

Type "q"
Sleep 1s
