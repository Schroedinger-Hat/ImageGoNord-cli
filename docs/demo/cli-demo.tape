# ImageGoNord CLI demo
# Recorded with VHS: https://github.com/charmbracelet/vhs

Output docs/demo/cli-demo.gif

Set Theme "nord"
Set FontSize 14
Set Width 1200
Set Height 700
Set Padding 12

# Anonymise the shell prompt
Type "export PS1='user@machine:~$ ' && clear"
Enter
Sleep 500ms

# --- doctor ---
Type "ign doctor"
Enter
Sleep 3s

# --- palette list ---
Type "ign palette list"
Enter
Sleep 2500ms

# --- single image convert ---
Type "cp /tmp/demo-input.png /tmp/wallpaper.png"
Enter
Sleep 300ms
Type "ign -i /tmp/wallpaper.png -o /tmp/wallpaper-nord.png"
Enter
Sleep 4s

# --- JSON output ---
Type "ign -i /tmp/wallpaper.png -o /tmp/wallpaper-nord.png --format=json"
Enter
Sleep 4s

# --- batch dry-run ---
Type "mkdir -p /tmp/images && cp /tmp/demo-input.png /tmp/images/photo1.png && cp /tmp/demo-input.png /tmp/images/photo2.png"
Enter
Sleep 500ms
Type "ign batch /tmp/images"
Enter
Sleep 3s

Sleep 2s
