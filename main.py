import json
import os
import datetime

def generate_post():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    content = f"""# Top AI Tools - {date_str}

Welcome to the daily roundup of the best AI tools and productivity hacks.

## 1. Automated Blogging
A tool that creates a blog and monetizes it entirely on its own.
[Try it here (Affiliate Link)](#)

## 2. AI Content Generator
Generate SEO-optimized content with a click.
[Sign up now (Affiliate Link)](#)

*More updates coming tomorrow!*
"""
    
    os.makedirs("posts", exist_ok=True)
    filename = f"posts/{date_str}-ai-tools.md"
    
    with open(filename, "w") as f:
        f.write(content)
        
    print(f"Generated {filename}")
    
    # Update index.html
    html_content = f"""<!DOCTYPE html>
<html>
<head><title>AI Money Machine</title></head>
<body>
<h1>Daily AI Tools & Hacks</h1>
<p>Latest Post: <a href="{filename}">{date_str} Updates</a></p>
<p><em>Automatically generated every day.</em></p>
</body>
</html>
"""
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_post()
