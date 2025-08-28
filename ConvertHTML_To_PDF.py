from weasyprint import HTML, CSS

def convert_html_file_to_pdf(html_file_path, pdf_output_path, css_file_path=None):
    """
    Converts an HTML file to a PDF, optionally applying a CSS file for formatting.

    Args:
        html_file_path (str): The path to the input HTML file.
        pdf_output_path (str): The path where the output PDF will be saved.
        css_file_path (str, optional): The path to an external CSS file for styling.
                                        If None, only inline and embedded CSS in HTML is used.
    """
    try:
        # Read the HTML content from the file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Create an HTML object
        html = HTML(string=html_content)

        # Apply external CSS if provided
        stylesheets = []
        if css_file_path:
            with open(css_file_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            stylesheets.append(CSS(string=css_content))

        # Write the PDF
        html.write_pdf(pdf_output_path, stylesheets=None )
        print(f"PDF successfully generated at: {pdf_output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example Usage:
# 1. Create an HTML file (e.g., 'example.html')
# 2. Create an optional CSS file (e.g., 'styles.css')

# example.html content:
# ```html
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Formatted PDF Example</title>
#     <link rel="stylesheet" href="styles.css">
# </head>
# <body>
#     <h1>Welcome to the Formatted PDF!</h1>
#     <p class="highlight">This paragraph should be highlighted according to the CSS.</p>
#     <ul>
#         <li>Item 1</li>
#         <li>Item 2</li>
#     </ul>
# </body>
# </html>
# ```

# styles.css content:
# ```css
# body {
#     font-family: Arial, sans-serif;
#     margin: 20px;
# }
# h1 {
#     color: #336699;
#     text-align: center;
# }
# .highlight {
#     background-color: #FFFF99;
#     padding: 10px;
#     border: 1px solid #CCCC66;
# }
# ```

# Call the function to convert
html_file = 'C:\\Users\\Mahesh\\Downloads\\CV Executive-saved (4).html'
css_file = 'C:\\Users\\Mahesh\\Downloads\\styles.css'
output_pdf = 'C:\\Users\\Mahesh\\Downloads\\CV Executive-saved (4).pdf'

# Ensure example.html and styles.css exist in the same directory as your script
convert_html_file_to_pdf(html_file, output_pdf, None)