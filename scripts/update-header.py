from datetime import datetime
import sys
import yaml

def get_ordinal(n: int) -> str:
    """Return ordinal string for an integer n (e.g., 1 -> '1st', 2 -> '2nd')."""

    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def format_date_with_ordinal(date: datetime) -> str:
    """Format date as 'Month Day<ordinal>, Year' (e.g., 'November 12th, 2025')."""

    month = date.strftime('%B')
    day = get_ordinal(date.day)
    year = date.year

    return f"{month} {day}, {year}"

def extract_metadata() -> dict[str, str]:
    """Extract project metadata from config."""

    try:

        with open("_config.yml", "r") as f:
        
            config = yaml.safe_load(f)
            # Get basic info
            title = config.get("title", "No Title")
            description = config.get("description", "No Description")
            author = config.get("author", "No Author")
            # Get current date in 'Month Day<ordinal>, Year' format
            current_date = format_date_with_ordinal(datetime.now())
            return {
                "title": title,
                "description": description,
                "author": author,
                "updated": current_date
            }
        
    except FileNotFoundError:

        print("Error: _config.yml not found")
        sys.exit(1)

    except yaml.YAMLError as e:

        print(f"Error parsing _config.yml: {e}")
        sys.exit(1)


def update_readme(metadata: dict[str, str]) -> None:
    """Update README.md with project metadata."""

    try:
        with open("README.md", "r") as f:
            # get all lines in the file
            lines = f.readlines()
            lines_to_remove = 0
            for line in lines:
                if line.strip() == "---":
                    break
                lines_to_remove += 1
            
            # Remove existing metadata block
            lines = lines[lines_to_remove:]  # +1 to remove the
            
            # Insert metadata at the top
            lines.insert(0, f"*Last Updated: {metadata['updated']}*\n\n")
            lines.insert(0, f"*Author: {metadata['author']}*\n\n")
            lines.insert(0, f"**{metadata['description']}**\n\n")
            lines.insert(0, f"# {metadata['title']}\n\n")
        
        # Write back to README.md
        with open("README.md", "w") as f:
            f.writelines(lines)
        
        print("README.md updated successfully.")

    except FileNotFoundError:
        print("Error: README.md not found")
        sys.exit(1)

if __name__ == "__main__":
    metadata = extract_metadata()
    update_readme(metadata)