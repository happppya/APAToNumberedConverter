# APA To Numbered Converter

This tool converts standard APA citation format of (Last, Date) to the numbered APA-like format required by JHSS.

Multiple authors and "et al." syntax is supported. But **for edge cases you need to do manual review!**

# Usage

Prepare your input files in the main directory:
- **input_bibliography.txt**: Your original APA references, each citation on its own new line. See the file in this repo for the example.
- **input_text.txt**: Your original APA paper. See the file in this repo for the example.

If you are using Google Docs:
- First separate your paper and references into two separate tabs
- Go to File > Download as Markdown, in order to get both as separate markdown files
- Open the two markdown files and copy paste their contents into the two respective input files
- This way, your output will also be in markdown
- Then, you can copy paste your output back into Google Docs with correct formatting with Right Click > Paste from Markdown

Run main.py.

Your output will appear in `output_bibliography.txt` and `output_paper.txt`.

If **manual review** is required, you can easily see which ones you need to fix in `output_bibliography.txt` which will display `[MANUAL REVIEW REQUIRED]` next to numbers where manual review is required. You can ctrl + f in your output paper to see where it's failing and to identify what the correct author name is. 

To perform manual review, edit the `author_overrides` dictionary defined in the `main` function in `main.py`. This is marked with the comment `# Add your manual overrides here`.

This dictionary maps incorrectly recognized names to the correct overrided version. For example, mine was:
```python
author_overrides = {
    "s": "Barnes", # In this example, it maps the incorrectly recognized "s" as "Barnes". This was happening because my paper had the text "Barnes's"
    "nkel": "Sünkel" # In this example, it can't recognize the u with the dots for some reason and was showing up as "nkel" when it should have been "Sünkel"
}
```

Keep running main.py until your output has no manual reviews.