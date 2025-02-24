import os
import re
import time
import asyncio
import aiohttp
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_DIR = r"G:\Ebooks"
EPUB_URL = "http://IPAddress:Port/get/EPUB/{}/Library" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MOBI_URL = "http://IPAddress:Port/get/MOBI/{}/Library" #Change this to your DNS\IP Address and port number of your Calibre Library. You may also have to change the "Calibre" at the end to match the name of the Library. If you go to download a book manually look the URL to find it.
MAX_CONCURRENT = 2  # Recommend leaving it at 2. It seems more stable at 2.
MAX_SCANID = 18460 # Change depending on how many books are in the library.
CHUNK_SIZE = 8192  # Increased from 1024 for better performance

# Compile regex patterns once
FILENAME_UTF8_PATTERN = re.compile(r"filename\*=UTF-8''(.+)")
FILENAME_QUOTED_PATTERN = re.compile(r'filename=["\'](.*?)(?:["\']\s*$|$)')
FILENAME_PLAIN_PATTERN = re.compile(r'filename=([^;\n]+)')
SANITIZE_PATTERN = re.compile(r'[\\/*?:"<>|]')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

def sanitize_filename(filename):
    """Optimized filename sanitization."""
    name, ext = os.path.splitext(filename)
    name = (name.replace("&#x27;", "'")
               .replace("&#39;", "'")
               .replace("&amp;", "&")
               .strip()
               .replace(";", ""))
    
    name = SANITIZE_PATTERN.sub("", name)
    name = name.replace("..", ".")
    return (name[:240] + ext) if len(name) > 240 else (name + ext)

def extract_filename(response, book_id):
    """Optimized filename extraction."""
    content_disposition = response.headers.get("Content-Disposition", "")
    
    if not content_disposition:
        return f"Book_{book_id}.epub"
    
    for pattern in [FILENAME_UTF8_PATTERN, FILENAME_QUOTED_PATTERN, FILENAME_PLAIN_PATTERN]:
        match = pattern.search(content_disposition)
        if match:
            filename = urllib.parse.unquote(match.group(1))
            return sanitize_filename(filename.split('.epub')[0] + '.epub')
    
    return f"Book_{book_id}.epub"

async def download_book(session, book_id):
    """Asynchronous book download function."""
    filepath = os.path.join(DOWNLOAD_DIR, f"Book_{book_id}.epub")
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"⏭️ Skipping #{book_id}: File already exists")
        return True

    urls = [EPUB_URL.format(book_id), MOBI_URL.format(book_id)]
    
    for url in urls:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    continue

                filename = extract_filename(response, book_id)
                filepath = os.path.join(DOWNLOAD_DIR, filename)

                with open(filepath, "wb") as f:
                    async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)

                display_name = os.path.splitext(filename)[0]
                parts = display_name.split(' - ')
                title = parts[0]
                author = parts[1].split('_')[0] if len(parts) > 1 else "Unknown Author"
                
                print(f"✅ Downloaded #{book_id}: {title} by {author}")
                return True

        except aiohttp.ClientError:
            continue
        except Exception as e:
            print(f"⚠️ Error downloading #{book_id}: {str(e)}")
            continue
    
    print(f"❌ Book {book_id} not found")
    return False

async def download_all_books(start_id=MAX_SCANID, end_id=1):
    """Asynchronous main download coordinator."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for book_id in range(start_id, end_id - 1, -1):
            # Add small delay between task creation to prevent overwhelming
            await asyncio.sleep(0.1)
            tasks.append(download_book(session, book_id))
            
            # Process in batches to manage memory
            if len(tasks) >= MAX_CONCURRENT:
                await asyncio.gather(*tasks)
                tasks = []
        
        # Process remaining tasks
        if tasks:
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(download_all_books(MAX_SCANID, 1))
