import os
import json
import requests
import logging
from typing import List, Optional
from mcp.server.fastmcp import FastMCP

# Configure logging to avoid printing to stdout, as recommended for MCP servers.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the FastMCP server with a descriptive name.
# This name will be visible to clients connecting to your MCP server.
mcp = FastMCP("DevToBlogPublisher")

@mcp.tool()
def publish_blog_to_devto(
    title: str,
    body_markdown: str,
    tags: Optional[List[str]] = None,
    published: bool = False,
    series: Optional[str] = None,
    canonical_url: Optional[str] = None,
    cover_image: Optional[str] = None
) -> str:
    """
    Publishes a blog post to dev.to.

    Args:
        title (str): The title of the blog post.
        body_markdown (str): The content of the blog post in Markdown format.
        tags (Optional[List[str]]): A list of tags for the blog post (e.g., ["python", "webdev"]).
        published (bool): Set to True to publish immediately, False to save as a draft.
        series (Optional[str]): The name of the series this article belongs to.
        canonical_url (Optional[str]): The canonical URL of the article if it's cross-posted.
        cover_image (Optional[str]): URL of the cover image for the article.

    Returns:
        str: A message indicating the success or failure of the publishing operation,
             including the article URL if successful.
    """
    logging.info(f"Attempting to publish blog post: '{title}' to dev.to")

    # Retrieve the Dev.to API key from environment variables.
    # It's crucial to keep your API key secure and not hardcode it.
    devto_api_key = os.getenv("DEVTO_API_KEY")
    if not devto_api_key:
        logging.error("DEVTO_API_KEY environment variable not set.")
        return "Error: DEVTO_API_KEY environment variable is not set. Please set it to publish articles."

    # Dev.to API endpoint for creating articles.
    DEVTO_API_URL = "https://dev.to/api/articles"

    # Prepare the headers for the API request.
    headers = {
        "Content-Type": "application/json",
        "api-key": devto_api_key
    }

    # Construct the article data payload.
    article_data = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "published": published,
        }
    }

    # Add optional fields if they are provided.
    if tags:
        article_data["article"]["tags"] = tags
    if series:
        article_data["article"]["series"] = series
    if canonical_url:
        article_data["article"]["canonical_url"] = canonical_url
    if cover_image:
        article_data["article"]["cover_image"] = cover_image

    try:
        # Make the POST request to the Dev.to API.
        response = requests.post(DEVTO_API_URL, headers=headers, json=article_data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response.
        response_json = response.json()

        if response.status_code == 201:
            article_url = response_json.get("url")
            logging.info(f"Article '{title}' published successfully! URL: {article_url}")
            return f"Article published successfully! URL: {article_url}"
        else:
            error_message = response_json.get("error", "Unknown error")
            logging.error(f"Failed to publish article '{title}'. Status code: {response.status_code}, Error: {error_message}")
            return f"Failed to publish article. Status code: {response.status_code}, Error: {error_message}"

    except requests.exceptions.RequestException as e:
        logging.error(f"Network or API request error: {e}")
        return f"An error occurred during the API request: {e}"
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"

@mcp.prompt("blog_post_generator_prompt")
def blog_post_generator_prompt(topic: str) -> str:
    """
    A prompt template to guide the LLM in generating a blog post.

    Args:
        topic (str): The main topic of the blog post.

    Returns:
        str: A Markdown-formatted prompt for generating a blog post.
    """
    
    return f"""
# Generate a Dev.to Blog Post

Please generate a comprehensive and engaging blog post about the following topic: **{topic}**.

The blog post should include:
- A catchy and informative title.
- An introduction that hooks the reader.
- Several paragraphs discussing key aspects of the topic.
- Code examples or technical details if applicable.
- A conclusion that summarizes the main points and offers a call to action or further thoughts.
- Use Markdown formatting extensively (headings, bold, italics, code blocks, lists).

Consider the target audience to be developers and tech enthusiasts on Dev.to.
"""


# This block ensures the MCP server runs when the script is executed directly.
if __name__ == "__main__":
    logging.info("Starting Dev.to Blog Publisher MCP Server...")
    mcp.run(transport='stdio')

