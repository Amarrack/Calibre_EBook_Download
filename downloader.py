import os
import requests
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Detect the desktop path dynamically for any user
USER_DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
DOWNLOAD_DIR = os.path.join(USER_DESKTOP, "Downloaded_Ebooks")
EPUB_URL = "http://IPAddress:Port/get/EPUB/{}/Library" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MOBI_URL = "http://IPAddress:Port/get/MOBI/{}/Library" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MAX_THREADS = 10  # Adjust for performance
MAX_SCANID = 8000

def sanitize_filename(filename):
    """ Cleans up filenames by removing invalid characters for Windows. """
    filename = filename.strip().replace(";", "")  # Remove any trailing semicolons
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)  # Remove forbidden characters
    filename = filename.replace("..", ".")  # Prevent path traversal issues
    return filename

def extract_filename(response, book_id):
    """ Extracts the filename from the response headers, falls back if needed. """
    content_disposition = response.headers.get("Content-Disposition")
    
    if content_disposition:
        match = re.search(r'filename\*?=["\']?(?:UTF-8\'\')?([^"\']+)["\']?', content_disposition, re.IGNORECASE)
        if match:
            filename = urllib.parse.unquote(match.group(1))  # Decode percent-encoded characters
            return sanitize_filename(filename)
    
    # Fallback if no filename is found
    return f"Book_{book_id}.epub"

def download_book(book_id):
    """ Attempts to download a book and saves it with its original filename. """
    urls = [EPUB_URL.format(book_id), MOBI_URL.format(book_id)]
    
    for url in urls:
        try:
            response = requests.get(url, stream=True, timeout=10)
            
            if response.status_code == 200:
                filename = extract_filename(response, book_id)
                filepath = os.path.join(DOWNLOAD_DIR, filename)

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)
                
                print(f"✅ Downloaded: {filename}")
                return  # Exit function after successful download
            
        except Exception as e:
            continue  # Try next URL if this one fails
    
    # If we get here, both URLs failed
    print(f"❌ Book {book_id} not found (HTTP 404)")

def download_all_books(start_id=1000, end_id=1):
    """ Loops through book IDs and downloads them using multiple threads. """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)  # Ensure folder exists

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_book = {executor.submit(download_book, book_id): book_id for book_id in range(start_id, end_id - 1, -1)}

        for future in as_completed(future_to_book):
            book_id = future_to_book[future]
            try:
                future.result()
            except Exception as e:
                print(f"⚠️ Unexpected error on Book {book_id}: {e}")

if __name__ == "__main__":
    download_all_books(MAX_SCANID, 1)  # Adjust range as needed
