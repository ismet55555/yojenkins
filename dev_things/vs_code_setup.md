# Visual Studio Code Setup

Here included are some general suggestions for setting up your VS Code environment in order
to operate and contribute on this project. *Note that these are mare suggestions, everyone tends
to have their own tools and ways of doing things.*

---

## Extensions

### **Interpretation and Formatting**
- Python
- Better TOML
- TOML Language Support
- YAML
- XML

### **git**
- Git Graph
- GitLens

### **Code Assistance**
- Pylance
- Visual Studio IntelliCode
- Path Intellisense

### **Other**
- Docker

---

## Settings

- **User Settings**
    - Settings applied glabally to the user
    - To edit: `Ctrl + Shift + P` type: `Preferences: Open Settings (JSON)`

- **Workspace Settings**
    - Settings applied for a current workspace or project
    - To edit: `Ctrl + Shift + P` type: `Preferences: Open Workspace Settings (JSON)`


### Show `.git` directory
```json
    "files.exclude": {
        "**/.git": false
    }
```

### Increase Terminal Scroll Back History
```json
"terminal.integrated.scrollback": 5000,
```

### Increase the Visibility of Schroll Bars
```json
    "editor.scrollbar.verticalScrollbarSize": 30,
    "editor.scrollbar.horizontal": "visible",
    "editor.scrollbar.horizontalScrollbarSize": 30,
```


### Add a Vertical Line at Line Length / Column Position
```json
    "editor.rulers": [120],
```
