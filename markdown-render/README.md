# Markdown Render

## Running Generation Script

### create venv
```bash
python3 -m venv venv 
```
### activate venv
``` bash
source venv/bin/activate
```

### install requirements
```bash
(venv) pip3 install -r requirements.txt
```

### to render
```bash
(venv) python3 render-markdown.py  
```

## Writing Articles

### Creating Files
To create a new article insert a new directory at in the articles folder.  

Once you have that create a new **index.md** file. This is what the parser will read when output as a new **index.html** file.  


### File Structure
The **index.md** file is split into 2 seconds *MetaData* and *Markdown Content*. Understanding how to format the metadata is critical for generating the html file.  

```
<!--MetaData
Title: str
Published: Month Day, Year 
Edited: Month Day, Year
Preview:\n
[Str or none]
-->
```

The formatting is very specific.  
*Title, Published, edited* must be a single line. The spelling and : must be exact. Preview is the only one that can be multiple lines, but the content cannot be on the same line as the *Preview:* declaration.

**Title**  
**Published**  
**Edited**  
**Preview**  

Everything after MetaData will be considered as *markdown* content and will be rendered as such.