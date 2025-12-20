import markdown
from pathlib import Path
from datetime import datetime

ARTICLES_DIR = Path("../articles")

def template_inserter(template_file_path: Path, insert_str: str) -> str:
    with open(template_file_path, 'r') as file:
        lines = file.readlines()

        try:
            insert_idx = lines.index("<!--INSERT-->\n")
        except ValueError:
            raise ValueError("<!--INSERT-->\n not found. Please ensure it is in this exact form as a string (no front spacing)")

        output = "".join(lines[:insert_idx]) + insert_str + "".join(lines[insert_idx+1:])
        return output


class Article:
    def __init__(self, 
                 title: str, published_date: str, published_time, 
                 edited_date: str, preview_content: str, 
                 markdown_content: str, directory: str):
        self.title = title
        self.published_date = published_date
        self.published_time = published_time
        self.edited_date = edited_date
        self.preview_content = preview_content
        self.markdown_content = markdown_content
        self.directory = directory

def parse_markdown_via_article_directory(directory: Path) -> Article:
    """
    Each index.md file has meta data in the following form
    <!--Metadata
    Title: (singular line) --> title of article
    Published: (singular line) --> date published "%B %d, %Y"
    Edited: (singular line) --> date edited "%B %d, %Y"
    Preview:
    (multiple line) --> preview (must have \n on preview)
    -->
    (Markdown)
    """
    DATE_FORMAT_PATTERN = "%B %d, %Y"
    file_path = directory / Path("index.md")

    with open(file_path, 'r') as file:
        def syntax_check(got: str, expected: str, equals=False) -> str:
            if equals and not got==expected:
                raise SyntaxError(f"{file_path}: (Expected: {expected}) Incorrect Markdown Syntax")

            if not equals and not got.startswith(expected):
                raise SyntaxError(f"{file_path}: (Expected: {expected}) Incorrect Markdown Syntax")

            return got

        lines = file.readlines(); num_lines = len(lines)

        # collecting lines and syntax checks
        meta_init_line = syntax_check(
            got=lines[0].strip(), # clean spaces and \n for equals = true
            expected="<!--MetaData",
            equals=True) 

        title_line = syntax_check(
            got=lines[1],
            expected="Title:")

        published_line = syntax_check(
            got=lines[2],
            expected="Published:")

        edited_line = syntax_check(
            got=lines[3],
            expected="Edited:")
        
        # syntax check Preview line
        preview_line = syntax_check(
            got=lines[4].strip(), # strip spaces and \n
            expected="Preview:",
            equals=True
        )

        # pull preview information
        header_ends = False

        # start at 5 because 4 is Preview: 
        tracker = 5
        while tracker < num_lines:
            if lines[tracker].strip() == "-->":
                header_ends = True
                tracker += 1
                break

            tracker += 1

        # check if metadata ends
        if not header_ends:
            raise SyntaxError(f"{file_path} expected header to end with -->, but never encountered")

        # pull contents 
        preview_content = "".join(lines[5:tracker-1]).strip()
        markdown_content = "".join(lines[tracker:])
      

        # parse the metadata
        title = title_line.split("Title:")[1].strip() # title

        published_date = published_line.split("Published:")[1].strip()
        published_time = datetime.strptime(published_date, DATE_FORMAT_PATTERN)

        edited_date = edited_line.split("Edited:")[1].strip()

        return Article(
            title=title, 
            published_date=published_date, 
            published_time=published_time, 
            edited_date=edited_date, 
            preview_content=preview_content, 
            markdown_content=markdown_content,
            directory=directory.name)

def generate_article_homepage_html_file(articles: list[Article]):
    def generate_entry(article: Article):
        return f"<div><a href=\"/articles/{article.directory}/\" title=\"{article.preview_content}\">{article.title}</a>: {article.published_date}</div>\n"

    TEMPLATE_FILE = ARTICLES_DIR / Path("template-homepage.html")

    entries = []
    for article in articles:
        entries.append(generate_entry(article))
    
    output = template_inserter(
        TEMPLATE_FILE, 
        "".join(entries))
        
    OUTPUT_FILE = ARTICLES_DIR / Path("index.html")
    with open(OUTPUT_FILE, 'w') as file:
        file.write(output)
    print("successfully generate homepage")

def generate_article_html_file(article: Article):
    TEMPLATE_FILE = ARTICLES_DIR / Path("template-article.html")
    
    output = template_inserter(
        TEMPLATE_FILE, 
        markdown.markdown(article.markdown_content))
 
    OUT_PATH = ARTICLES_DIR / Path(article.directory) / Path("index.html")
    with open(OUT_PATH, 'w') as file:
        file.write(output)
    print("successfully generate article", OUT_PATH)

# html = markdown.markdown("#hello")
parsed_articles = []

for entry in ARTICLES_DIR.iterdir():
    # build all directories
    if entry.is_dir():
        # concat root with current article directory
        parsed_articles.append(
            parse_markdown_via_article_directory(ARTICLES_DIR / Path(entry.name))) 

# sort articles via most recent via published_time
parsed_articles.sort(
    reverse=True, 
    key=lambda item: item.published_time)

# step 1: generate article homepage
generate_article_homepage_html_file(parsed_articles)

# step 2: generate index.html for each article
for article in parsed_articles:
    generate_article_html_file(article)