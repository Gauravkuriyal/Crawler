import requests
import re
import os
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import fitz  # PyMuPDF for PDFs
import docx  # python-docx for DOCX files
import openpyxl  # openpyxl for XLSX files
import csv
from collections import deque
from urllib.parse import urlparse
import mimetypes
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import BytesIO
# from playwright.sync_api import sync_playwright


headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
# Regular expressions for emails and phone numbers
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
# PHONE_REGEX = r"\+\d{1,4}[\s-]?\(?\d{1,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}"
allowed =["1","7","20","27","30","31","32","33","34","36","39","40","41","43","44","45","46","47","48","49","51","52","53","54","55","56","57","58","60","61","62","63","64","65","66","81","82","84","86","90","91","92","93","94","95","98","211","212","213","216","218","220","221","222","223","224","225","226","227","228","229","230","231","232","233","234","235","236","237","238","239","240","241","242","243","244","245","246","248","249","250","251","252","253","254","255","256","257","258","260","261","262","263","264","265","266","267","268","269","290","291","297","298","299","350","351","352","353","354","355","356","357","358","359","370","371","372","373","374","375","376","377","378","379","380","381","382","383","385","386","387","389","420","421","423","500","501","502","503","504","505","506","507","508","509","590","591","592","593","595","597","598","599","670","672","673","674","675","676","677","678","679","680","681","682","683","685","686","687","688","689","690","691","692","850","852","853","855","856","880","886","960","961","962","963","964","965","966","967","968","970","971","972","973","974","975","976","977","992","993","994","995","996","998","1-242","1-246","1-264","1-268","1-284","1-340","1-345","1-441","1-473","1-649","1-664","1-670","1-671","1-684","1-721","1-758","1-767","1-784","1-787, 1-939","1-809, 1-829, 1-849","1-868","1-869","1-876","44-1481","44-1534","44-1624"]
country_group = "|".join(allowed) 
PHONE_REGEX = rf"\+(?:{country_group})[\s-]?\(?\d{{1,4}}\)?[\s-]?\d{{3,4}}[\s-]?\d{{3,4}}"

# AllEmails = set()
# AllNumbers = set()
# visited_links = set()
download_folder = "downloaded_files"

# Create download folder if not exists
os.makedirs(download_folder, exist_ok=True)

def get_emails_and_phones(content):
    """Extract emails and phone numbers from page content"""
    emails = re.findall(EMAIL_REGEX, content)
    phones = re.findall(PHONE_REGEX, content)
    return set(emails), set(phones)

def extract_text_from_file(file_path, file_extension):
    """Extract text from different file types"""
    try:
        if file_extension == ".pdf":
            doc = fitz.open(file_path)
            text = "\n".join([page.get_text() for page in doc])
        elif file_extension == ".docx":
            doc = docx.Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif file_extension == ".xlsx":
            wb = openpyxl.load_workbook(file_path)
            text = "\n".join([" ".join([str(cell.value) for cell in row]) for sheet in wb.worksheets for row in sheet.iter_rows()])
        elif file_extension == ".csv":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as csvfile:
                reader = csv.reader(csvfile)
                text = "\n".join([" ".join(row) for row in reader])
        else:  # Treat as plain text
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                text = file.read()
        return text
    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")
        return ""

def process_uploaded_file(file_path):
    AllEmails = set()
    AllNumbers = set()
    """Process an uploaded file and extract emails and phone numbers"""
    file_extension = os.path.splitext(file_path)[1].lower()
    text = extract_text_from_file(file_path, file_extension)
    emails, phones = get_emails_and_phones(text)
    AllEmails.update(emails)
    AllNumbers.update(phones)
    print("\n📧 Extracted Emails:", AllEmails)
    print("\n📞 Extracted Phone Numbers:", AllNumbers)

    return AllEmails, AllNumbers

def download_and_extract(url):
    """Download a file and extract content"""
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    file_extension = os.path.splitext(url)[1].lower()
    if file_extension not in [".pdf", ".docx", ".xlsx", ".csv", ".txt"]:
        return  # Skip unsupported file types

    filename = os.path.join(download_folder, os.path.basename(url))
    try:
        response = requests.get(url, headers=headers,timeout=10)
        response.raise_for_status()
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"📂 Downloaded: {filename}")

        text = extract_text_from_file(filename, file_extension)
        emails, phones = get_emails_and_phones(text)
        # AllEmails.update(emails)
        # AllNumbers.update(phones)
        return emails,phones

    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return (set(),set())

# def crawl(url, base_domain):
def crawl(start_url, base_domain,visited_links, max_depth=10):
    """Recursively crawl a website to extract emails and phone numbers"""
    AllEmails = set()
    AllNumbers = set()
    # new
    queue = deque([(start_url, 0)])

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    while queue:
        url, depth = queue.popleft()

        if url in visited_links:
            continue

        if depth > max_depth:
            continue

        print(f"🔍 Crawling: {url}")
        visited_links.add(url)

        try:
            response = requests.get(url, headers=headers,timeout=5)
            response.raise_for_status()
            content = response.text
        except requests.RequestException:
            print(f"❌ Failed to access: {url}")
            continue
        except Exception as e:
            print(f"❌ Failed to access: {url}")
            continue


        # Extract emails and phone numbers
        emails, phones = get_emails_and_phones(content)
        # AllEmails.update(emails)
        # AllNumbers.update(phones)
        if emails or phones:
            AllEmails.update(emails)
            AllNumbers.update(phones)

        # Parse links in the page
        soup = BeautifulSoup(content, "html.parser")
        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            extracted_domain = tldextract.extract(next_url).registered_domain

            if extracted_domain == base_domain and next_url not in visited_links:
                if any(next_url.endswith(ext) for ext in [".pdf", ".docx", ".xlsx", ".txt", ".csv"]):
                    emails, phones = download_and_extract(next_url)
                    AllEmails.update(emails)
                    AllNumbers.update(phones)
                else:
                    queue.append((next_url, depth + 1))

    print("\nCrawling completed.")
    print("\n📧 Extracted Emails:", AllEmails)
    print("📞 Extracted Phone Numbers:", AllNumbers)
    return AllEmails, AllNumbers

def site_crawler(site_url):
    try:
        # global AllNumbers, AllEmails
        # AllEmails = set()
        # AllNumbers = set()
        visited_links = set()
        start_url = site_url.strip()
        base_domain = tldextract.extract(start_url).registered_domain
        crawl(start_url, base_domain,visited_links)
        return (AllEmails,AllNumbers)
    except Exception as e:
        print(e)
        return (set(),set())
    finally:
        AllEmails = set()
        AllNumbers = set()

def file_crawler(file_path):
    try:
        emails = set()
        numbers = set()
        file_path = file_path.strip()
        if os.path.exists(file_path):
            emails,numbers = process_uploaded_file(file_path)
        else:
            print("❌ File not found. Please enter a valid file path.")
        return (emails,numbers)
    except Exception as e:
        print(e)
        return (set(),set())

    
# if __name__ == "__main__":
#     print("Choose an option:")
#     print("1️⃣ Crawl a website for emails & phone numbers")
#     print("2️⃣ Upload a file and extract emails & phone numbers")
#     choice = input("Enter your choice (1 or 2): ").strip()
    
#     if choice == "1":
#         start_url = input("Enter a website URL to crawl: ").strip()
#         base_domain = tldextract.extract(start_url).registered_domain
#         crawl(start_url, base_domain)

#         print("\n📧 Extracted Emails:")
#         print(AllEmails)
#         print("\n📞 Extracted Phone Numbers:")
#         print(AllNumbers)

#     elif choice == "2":
#         file_path = input("Enter the path of the file to upload: ").strip()
#         if os.path.exists(file_path):
#             process_uploaded_file(file_path)
#         else:
#             print("❌ File not found. Please enter a valid file path.")
#     else:
#         print("❌ Invalid choice. Please enter 1 or 2.")


def crawl_urls_for_files(urls, visited_urls=None):
    """
    Crawls webpages from a list of URLs, downloads supported files (including those without extensions),
    and extracts emails and phone numbers. Also crawls URLs linked from anchor tags with inner text 'pdf'.
    Args:
        urls (list): List of webpage URLs to scrape for files.
        visited_urls (set): Set of URLs already visited to prevent infinite loops (default: None).
    Returns:
        tuple: (set of emails, set of phone numbers) extracted from all downloaded files.
    """
    if visited_urls is None:
        visited_urls = set()

    emails = set()
    phone_numbers = set()
    
    # Define valid extensions and their corresponding MIME types
    valid_mime_types = {
        'application/pdf': '.pdf',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        'application/vnd.ms-excel': '.xls',
        'text/csv': '.csv',
        'application/msword': '.doc',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        'text/plain': '.txt',
    }

    # Set user-agent to avoid being blocked
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # headers = {
    #     "Accept": "*/*",
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    # }

    # Set up retry strategy for requests
    session = requests.Session()
    retries = Retry(total=1, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    def sanitize_filename(filename):
        """Sanitize filename to remove invalid characters and handle UTF-8 encoding."""
        if 'filename*=' in filename:
            try:
                filename = filename.split("filename*=UTF-8''")[-1]
                filename = requests.utils.unquote(filename)
            except Exception:
                pass
        filename = re.sub(r'[^\w\.\-]', '_', filename)
        filename = filename.strip('._')
        return filename or 'downloaded_file'

    def process_webpage(url):
        """Helper function to process a single webpage and return file URLs and PDF-linked URLs."""
        file_urls = set()
        pdf_linked_urls = set()
        
        try:

            content_type = url.split(".")[-1]
            if content_type in ['pdf','xlsx','xls','csv','doc','docx','txt']:
                file_urls.add(url)
                
                return file_urls,pdf_linked_urls


            # Fetch the webpage
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links on the webpage
            links = soup.find_all('a', href=True)
            for link in set(links):
                href = link['href']
                file_url = urljoin(url, href)

                # Check if the link points to a supported file type
                try:
                    # head_response = session.head(file_url, headers=headers, timeout=10, allow_redirects=True)
                    # content_type = head_response.headers.get('content-type', '').lower().split(';')[0]
                    content_type = href.split(".")[-1]
                    
                    # if content_type in valid_mime_types:
                    if content_type in ['pdf','xlsx','xls','csv','doc','docx','txt']:
                        file_urls.add(file_url)
                    # else:
                    #     ext = os.path.splitext(urlparse(file_url).path)[1].lower()
                    #     if ext in valid_mime_types.values():
                    #         file_urls.add(file_url)

                except requests.RequestException as e:
                    print(f"Error checking Content-Type for {file_url}: {e}")
                    continue

                link_text = link.get_text().strip().lower()
                link_title = link.get("title")
                if link_title:
                    link_title = link_title.strip().lower()
                    print(f"link title is {link_title} for link: {file_url}")
                # Check if the link text is exactly 'pdf'
                print(f"link text is {link_text[:10]} for link: {file_url}")
                if link_text == 'pdf' or link_text == 'full article' or link_text == 'view pdf' or link_title ==  "article pdf" or link_title == "view full article":
                    # print(f"link text is {link_text[:10]} for link: {file_url}")
                    if file_url not in visited_urls:
                        pdf_linked_urls.add(file_url)
                    continue

        except requests.RequestException as e:
            print(f"Error fetching webpage {url}: {e}")
        except Exception as e:
            print(f"Unexpected error for webpage {url}: {e}")

        return file_urls, pdf_linked_urls

    # Process each input URL
    for url in urls:
        url = url.replace('"', '')
        print("Processing URL:", url)
        
        if url in visited_urls:
            print(f"Skipping already visited URL: {url}")
            continue
        
        visited_urls.add(url)
        file_urls, pdf_linked_urls = process_webpage(url)
        print(f"found Urls\n file urls:  {file_urls},\n pdf_linked_urls:  {pdf_linked_urls}")

        try: 
            response = requests.get(url)
            response.raise_for_status()
            full_text = response.text
            Nemails, NphoneNumbers = get_emails_and_phones(full_text)
            print(f"from {url} webpage {Nemails} , {NphoneNumbers}")
            emails.update(Nemails)
            phone_numbers.update(NphoneNumbers)
        except Exception as e:
            print(f"Unexpected error for webpage {url}: {e}")

        # Download and process files from the current webpage
        for file_url in file_urls:
        # for file_url in ["https://theaspd.com/index.php/ijes/article/download/11836/8440/25192"]:
        # for file_url in ["https://theaspd.com/index.php/ijes/article/view/11836/8440"]:
            try:
                # file_url = "https://api.iarapublication.com/media/books/book_pdf/indian-banking-system-case-studies-of-indian-banking-sector.pdf"
                file_response = session.get(file_url, headers=headers, timeout=15)
                file_response.raise_for_status()

                # content_type = file_response.headers.get('content-type', '').lower().split(';')[0]
                # ext = valid_mime_types.get(content_type)
                # if not ext:
                #     ext = os.path.splitext(urlparse(file_url).path)[1].lower()
                #     if ext not in valid_mime_types.values():
                #         print(f"Skipping unsupported file type for {file_url}")
                #         continue

                # content_disposition = file_response.headers.get('content-disposition', '')
                # print(file_response.headers)
                # if content_disposition and 'filename=' in content_disposition:
                #     filename = content_disposition.split('filename=')[-1].strip('"\'')
                # else:
                #     filename = os.path.basename(urlparse(file_url).path)
                
                # filename = sanitize_filename(filename)
                # if not filename or not os.path.splitext(filename)[1]:
                #     filename = f'downloaded_file{ext}'
                # elif os.path.splitext(filename)[1].lower() != ext:
                #     filename = os.path.splitext(filename)[0] + ext

                # os.makedirs('media', exist_ok=True)
                # file_path = f'media/{filename}'

                # print("file_response ",)
                pdf_document = fitz.open(stream=file_response.content, filetype="pdf")
                full_text = ""
                for page in pdf_document:
                    full_text += page.get_text()

                # print(full_text[:10])
                # print(pdf_document.get_text())
                # pdf_document.close()
                # data = b''.join(file_response.iter_content(chunk_size=8192))


                # print("from file data",get_emails_and_phones(file_response.content))
                # with open(file_path, 'wb') as f:
                #     for chunk in file_response.iter_content(chunk_size=8192):
                #         if chunk:
                #             f.write(chunk)

                try:
                    # Nemails, NphoneNumbers = file_crawler(file_path)
                    if full_text:
                        if len(full_text)>0:
                            Nemails, NphoneNumbers = get_emails_and_phones(full_text)
                            emails.update(Nemails)
                            phone_numbers.update(NphoneNumbers)
                            print(f"Successfully processed {file_url} {Nemails} {NphoneNumbers}")
                except Exception as e:
                    print(f"Error crawling file {file_url}: {e}")

            except requests.RequestException as e:
                print(f"Error downloading file from {file_url}: {e}")
            except Exception as e:
                print(f"Unexpected error for file {file_url}: {e}")

        # Recursively crawl URLs linked from 'pdf' anchor tags
        # pdf_linked_urls.add(url)
        if pdf_linked_urls:
            print(f"Found PDF-linked URLs to crawl: {pdf_linked_urls}")
            # continue
            for pdf_linked_url in pdf_linked_urls:
                
                try:
                    # head_response = session.head(pdf_linked_url, headers=headers, timeout=10, allow_redirects=True)
                    # content_type = head_response.headers.get('content-type', '').lower().split(';')[0]
                    # print("content-type ",content_type)
                    html = requests.get(pdf_linked_url)
                    content_type = html.headers.get("Content-Type")

                    if content_type in valid_mime_types:
                        try:  
                            file_response = session.get(pdf_linked_url, headers=headers, timeout=10)
                            file_response.raise_for_status()

                            pdf_document = fitz.open(stream=file_response.content, filetype="pdf")
                            full_text = ""
                            for page in pdf_document:
                                full_text += page.get_text()

                            try:
                                # Nemails, NphoneNumbers = file_crawler(file_path)
                                Nemails, NphoneNumbers = get_emails_and_phones(full_text)
                                emails.update(Nemails)
                                phone_numbers.update(NphoneNumbers)
                                print(f"Successfully processed {pdf_linked_url} {Nemails} {NphoneNumbers}")
                            except Exception as e:
                                print(f"Error crawling file {pdf_linked_url}: {e}")
                        
                        except Exception as e:
                            print(f"Error getting file {pdf_linked_url}: {e}")


                    else:
                        html = html.text
                        soup = BeautifulSoup(html, "html.parser")
                        # Find all links on the webpage
                        links = soup.find_all('a', href=True)
                        for link in set(links):
                            href = link['href']
                            file_url = urljoin(url, href)
                            # Check if the link text is exactly 'pdf'
                            try:   
                                head_response = session.head(file_url, headers=headers, timeout=10, allow_redirects=True)
                                content_type = head_response.headers.get('content-type', '').lower().split(';')[0]
                                print("content-type j ",content_type)

                                if content_type in valid_mime_types:
                                    try:  
                                        file_response = session.get(file_url, headers=headers, timeout=15)
                                        file_response.raise_for_status()

                                        pdf_document = fitz.open(stream=file_response.content, filetype="pdf")
                                        full_text = ""
                                        for page in pdf_document:
                                            full_text += page.get_text()

                                        try:
                                            # Nemails, NphoneNumbers = file_crawler(file_path)
                                            Nemails, NphoneNumbers = get_emails_and_phones(full_text)
                                            emails.update(Nemails)
                                            phone_numbers.update(NphoneNumbers)
                                            print(f"Successfully processed {file_url} {Nemails} {NphoneNumbers}")
                                        except Exception as e:
                                            print(f"Error crawling file {file_url}: {e}")
                                    
                                    except Exception as e:
                                        print(f"Error getting file {file_url}: {e}")

                            except Exception as e:
                                print(f"Error getting content type file {file_url}: {e}")

                    # pdf_url = None
                    # embed = soup.find("embed")
                    # if embed and embed.get("src"):
                    #     pdf_url = embed["src"]
                    # else:
                    #     iframe = soup.find("iframe")
                    #     print("iframe",iframe)
                    #     if iframe and iframe.get("src"):
                    #         print("ihih")
                    #         pdf_url = iframe["src"]

                    # if not pdf_url:
                    #     raise Exception("PDF link not found inside viewer page")
                    
                    # pdf_url = "https://theaspd.com/plugins/generic/pdfJsViewer/pdf.js/web/viewer.html?file=https%3A%2F%2Ftheaspd.com%2Findex.php%2Fijes%2Farticle%2Fdownload%2F11836%2F8440%2F25192"
                    # if pdf_url.startswith("/"):
                    #     pdf_url = urljoin(url, pdf_url)
                    # # pdf_url = urljoin(url, pdf_url)
                    
                    # if "file=" not in viewer_url:
                    #     raise Exception("Viewer URL does not contain file parameter")

                    # pdf_url_encoded = viewer_url.split("file=")[1]
                    # pdf_url = unquote(pdf_url_encoded)  # decode %2F etc.
                    # pdf_url = urljoin(url, pdf_url)     # convert relative → absolute if needed

                    # print("PDF URL:", pdf_url)

                    # print("PDF URL:", pdf_url)

                    # pdf_bytes = requests.get(pdf_url).content

                    # # Step 4: Extract text with PyMuPDF
                    # doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    # text = ""
                    # for page in doc:
                    #     text += page.get_text() + "\n"

                    # print("\n--- Extracted Text (first 500 chars) ---\n")
                    # print(text[:100])
                except Exception as e:
                    print(f"Error getting {pdf_linked_url}: {e}")
            # Recursively call the function for PDF-linked URLs
            # sub_emails, sub_phone_numbers = crawl_urls_for_files(pdf_linked_urls, visited_urls)
            # emails.update(sub_emails)
            # phone_numbers.update(sub_phone_numbers)

    return emails, phone_numbers