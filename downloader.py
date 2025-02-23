import os
import requests
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Detect the desktop path dynamically for any user
USER_DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
DOWNLOAD_DIR = os.path.join(USER_DESKTOP, "Downloaded_Ebooks")
BASE_URL = "http://IPAddress:PortNumber/get/EPUB/{}/Calibre" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MAX_THREADS = 25  # Adjust for performance
MAX_SCAN_ID = 20000  # Highest possible book ID to scan from

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

def book_exists(book_id):
    """ Checks if a book exists by sending a HEAD request. """
    url = BASE_URL.format(book_id)
    try:
        response = requests.head(url, timeout=5)  # HEAD is faster than GET for checking existence
        return response.status_code == 200
    except requests.RequestException:
        return False

def find_book_id_range():
    """ Multithreaded scan for the highest and lowest book ID. """
    print("🔍 Scanning for available book IDs (multithreaded) This may take a while...")

    def check_id(book_id):
        return book_id if book_exists(book_id) else None

    # Scan for highest ID
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_id = {executor.submit(check_id, book_id): book_id for book_id in range(MAX_SCAN_ID, 0, -1)}
        highest_id = next((future.result() for future in as_completed(future_to_id) if future.result()), None)

    if highest_id is None:
        print("❌ No books found in the library.")
        return None, None

    # Scan for lowest ID
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_id = {executor.submit(check_id, book_id): book_id for book_id in range(1, highest_id + 1)}
        lowest_id = next((future.result() for future in as_completed(future_to_id) if future.result()), None)

    print(f"📚 Found books from ID {lowest_id} to {highest_id}")
    return lowest_id, highest_id

def download_book(book_id):
    """ Attempts to download a book and saves it with its original filename. """
    url = BASE_URL.format(book_id)

    try:
        response = requests.get(url, stream=True, timeout=10)
        
        if response.status_code == 200:
            filename = extract_filename(response, book_id)
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Book {book_id} not found (HTTP {response.status_code})")

    except Exception as e:
        print(f"⚠️ Error downloading Book {book_id}: {e}")

def download_all_books():
    """ Automatically detects the available book range and downloads them. """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    lowest_id, highest_id = find_book_id_range()
    if lowest_id is None or highest_id is None:
        return

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_book = {executor.submit(download_book, book_id): book_id for book_id in range(highest_id, lowest_id - 1, -1)}

        for future in as_completed(future_to_book):
            book_id = future_to_book[future]
            try:
                future.result()
            except Exception as e:
                print(f"⚠️ Unexpected error on Book {book_id}: {e}")

if __name__ == "__main__":
    download_all_books()
