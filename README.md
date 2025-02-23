# Calibre Library Downloader

## Overview

This Python script allows you to **automatically scan and download** all available books from a **public Calibre-Web library**. It dynamically detects the available book IDs, downloads them in parallel using multithreading, and saves them with their original filenames.

⚠ **Warning:** This script is provided **as-is**, without any guarantees. **Use responsibly** and ensure you have permission to download from the target Calibre library.

---

## Features

- **Automatic book detection** – Finds the highest and lowest book IDs.
- **Multithreaded scanning & downloading** – Increases speed significantly.
- **Saves books with their original filenames** – No need for manual renaming.
- **Works on any system** – Dynamically sets the download directory to the user's Desktop.

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
   - Download the books to `Downloaded_Ebooks` on your Desktop

---

## Customization

You can modify the script to fit your needs:

### Change the Library URL

Replace the `BASE_URL` value with your target library:

```python
BASE_URL = "http://your-calibre-web-instance/get/EPUB/{}/Calibre"
```

### Adjust the Maximum Scanning Range

If your library has more books, change the `MAX_SCAN_ID`:

```python
MAX_SCAN_ID = 8000  # Adjust to scan up to however many books are in your library.
```

### Modify the Download Directory

By default, books are saved to `Downloaded_Ebooks` on the Desktop. Change `DOWNLOAD_DIR` if needed:

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
MAX_THREADS = 20  # Higher = faster downloads, but more strain on the server
```

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

