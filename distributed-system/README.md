# Internet GoMoKu Game

## Usage
### 1: Mark the Template Folder.
Mark `templates/` as Template Folder in Pycharm

### 2: Initialize the database
When under the project folder, run the following commanding line.

```flask --app app init-db``` 

This project uses sqlite and may need some configuration in Pycharm in order to use the database.

### 3: Replace the urls
Replace the url in the script line

```const socket = io.connect("http://192.168.31.173:5000");``` 

with your PC's ip and port in files

`templates/loginAndSign/login.html`

`templates/loginAndSign/sign.html`

`templates/gamePart/base.html`

### 4: Run the app.
```python app.py```