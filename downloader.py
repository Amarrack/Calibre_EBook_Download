import os
import requests
import re
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Detect the desktop path dynamically for any user
USER_DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
DOWNLOAD_DIR = os.path.join(USER_DESKTOP, "Downloaded_Ebooks")
EPUB_URL = "http://IPAddress:Port/get/EPUB/{}/Library" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MOBI_URL = "http://IPAddress:Port/get/MOBI/{}/Library" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MAX_THREADS = 5  # Adjust for performance
MAX_SCANID = 14030

def sanitize_filename(filename):
    """ Cleans up filenames by removing/replacing invalid characters for Windows. """
    # First decode any HTML entities (like &#x27; for apostrophe)
    filename = filename.replace("&#x27;", "'")
    filename = filename.replace("&#39;", "'")
    filename = filename.replace("&amp;", "&")
    
    # Split filename and extension before sanitizing
    name, ext = os.path.splitext(filename)
    
    # Remove any trailing semicolons
    name = name.strip().replace(";", "")
    
    # Replace problematic characters with safe alternatives
    # Keep apostrophes but remove other dangerous characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    
    # Prevent path traversal issues
    name = name.replace("..", ".")
    
    # Limit length to avoid potential issues
    if len(name) > 240:  # Windows max path is 260, leave some room for the path
        name = name[:240]
        
    # Reconstruct filename with extension
    return name + ext

def extract_filename(response, book_id):
    """ Extracts the filename from the response headers, falls back if needed. """
    content_disposition = response.headers.get("Content-Disposition", "")
    
    if content_disposition:
        # Try RFC 5987 encoded filename first
        match = re.search(r"filename\*=UTF-8''(.+)", content_disposition)
        if match:
            filename = urllib.parse.unquote(match.group(1))
            return sanitize_filename(filename)
            
        # Try regular filename with quotes, handling potential nested quotes
        # This pattern will look for the last quote or the end of the string
        match = re.search(r'filename=["\'](.*?)(?:["\']\s*$|$)', content_disposition)
        if match:
            filename = match.group(1)
            return sanitize_filename(filename)
            
        # Try without quotes
        match = re.search(r'filename=([^;\n]+)', content_disposition)
        if match:
            filename = match.group(1)
            return sanitize_filename(filename)
    
    # Fallback if no filename is found
    return f"Book_{book_id}.epub"



def download_book(book_id):
    """ Attempts to download a book and saves it with its original filename. """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }
    urls = [EPUB_URL.format(book_id), MOBI_URL.format(book_id)]
    
    for url in urls:
        try:
            response = requests.get(url, stream=True, timeout=10, headers=headers)
            response.raise_for_status()
            
            if response.status_code == 200:
                filename = extract_filename(response, book_id)
                filepath = os.path.join(DOWNLOAD_DIR, filename)

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                
                # Clean up the filename for display
                display_name = os.path.splitext(filename)[0]  # Remove file extension
                parts = display_name.split(' - ')
                title = parts[0]
                author = parts[1] if len(parts) > 1 else "Unknown Author"
                # Remove the book ID from author if present
                author = author.split('_')[0] if '_' in author else author
                
                print(f"✅ Downloaded #{book_id}: {title} by {author}")
                return True
            
        except requests.exceptions.RequestException as e:
            continue  # Try next URL if this one fails
        except Exception as e:
            continue
    
    print(f"❌ Book {book_id} not found (HTTP 404)")
    return False





def download_all_books(start_id=1000, end_id=1):
    """ Loops through book IDs and downloads them using multiple threads. """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure folder exists

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Add a small delay between submissions
        futures = []
        for book_id in range(start_id, end_id - 1, -1):
            future = executor.submit(download_book, book_id)
            futures.append((future, book_id))
            time.sleep(0.1)  # Small delay between submissions

        for future, book_id in futures:
            try:
                success = future.result()
                if not success:
                    print(f"Failed to download Book {book_id}")
            except Exception as e:
                print(f"⚠️ Unexpected error on Book {book_id}: {e}")


if __name__ == "__main__":
    download_all_books(MAX_SCANID, 1)  # Adjust range as needed
