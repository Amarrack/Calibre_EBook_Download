# Calibre Library Downloader

## Overview

This Python script allows you to **automatically scan and download** all available books from a **Calibre-Web library**. It downloads them in parallel using multithreading, and saves them with their original filenames to a folder of your choice.

⚠ **Warning:** This script is provided **as-is**, without any guarantees. **Use responsibly** and ensure you have permission to download from the target Calibre library.

---

## Features

- **Multithreaded downloading** – Increases speed significantly.
- **Saves books with their original filenames** – No need for manual renaming.

---

## Requirements

Ensure you have **Python 3.x** installed along with the required dependencies:

```sh
pip install requests
```

To enable **faster scanning and downloading**, install `concurrent.futures` (included in Python 3 by default):

```sh
pip install futures
```

---

## Usage

1. **Clone the repository**: (Or just download the .PY File)
   ```sh
   git clone https://github.com/YOUR_GITHUB_USERNAME/calibre-library-downloader.git
   cd calibre-library-downloader
   ```
2. **Run the script**:
   ```sh
   python downloader.py
   ```
   The script will:
   - Scan the library for available book IDs
   - Download the books to whatever you set in the `DOWNLOAD_DIR` it will also create the folder automatically.

---

## Customization

You can modify the script to fit your needs:

### Change the Library URL

Replace the `EPUB_URL` and `MOBI_URL` value with your target library: **NOTE: This can change depending on what was setup. Easiest way I've found is to go to a book, right click download and copy link address. Paste it into a text editor. For the examples below "Calibre" is the Library name. Just change it to whatever the final word is for the download link

```python
EPUB_URL = "http://your-calibre-web-instance/get/EPUB/{}/Calibre"
```
```python
MOBI_URL = "http://your-calibre-web-instance/get/EPUB/{}/Calibre"
```

### Adjust the Maximum Scanning Range

If your library has more books, change the `MAX_SCAN_ID`:

```python
MAX_SCAN_ID = 8000  # Adjust to scan up to however many books are in your library.
```

### Modify the Download Directory

```python
DOWNLOAD_DIR = "C:/Your/Custom/Path"
```
On Windows it may need to look something like this
```python
DOWNLOAD_DIR = r"C:\Users\Userprofile\Desktop\Downloaded Ebooks"
```


### Increase Download Speed

You can tweak `MAX_THREADS` to increase or decrease parallel downloads:

```python
MAX_THREADS = 2  # Higher = faster downloads, but more strain on the server. Anything above 5 seems to start erroring out.
```

---

## Issues but not really issues

This script only targets EPUB and MOBI books. If there are PDF's or any other book types in the library it will simply just error out and say book not found and skip that book ID.

---

## Disclaimer

This script is intended for **personal use only**. Do not use it for unauthorized access or distribution of copyrighted materials. The author is **not responsible** for any misuse, server issues, or potential violations of terms of service.

**Use at your own risk.**

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributions

Pull requests and improvements are welcome! If you encounter issues, please submit a GitHub issue.

Happy downloading! 🚀

