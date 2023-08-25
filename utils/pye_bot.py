import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
class WebScraperBot:
    def __init__(self, url,depth, read_documents_flag='no'):
        self.url = url
        self.read_documents_flag = read_documents_flag
        self.document_text = []
        self.text_content = []
        self.visited_links = set()
        self.depth = depth

    def scrape_page(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.get_text() if soup.title else ""
        metadata = self.extract_metadata(url)
        text_content = f"""
        Webpage Link: {url}, 
        Webpage Title: {title},
        Metadata: {metadata},
        {soup.get_text()} 
        """ 
        
        self.text_content.append(text_content)   

    def get_internal_links(self, url, depth=1):
        if int(depth) <= 0:
            return []
        internal_links = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            link_url = urljoin(url, link['href'])
            if link_url != url and urlparse(link_url).netloc == urlparse(url).netloc and link_url not in self.visited_links:
                self.visited_links.add(link_url)
                internal_links.append(link_url)
                self.scrape_page(link_url)
                internal_links.extend(self.get_internal_links(link_url))

        return internal_links

    def get_external_links(self, url, depth=1):
        if int(depth) <= 0:
            return []
        external_links = []
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            try:
                link_url = urljoin(url, link['href'])
                if link_url != url and urlparse(link_url).netloc != urlparse(url).netloc and link_url not in self.visited_links:
                    self.visited_links.add(link_url)
                    external_links.append(link_url)
                    self.scrape_page(link_url)
                    external_links.extend(self.get_external_links(link_url))
            except Exception as e:
                print(f"Link: {link['href']}, caused error: {e}\n")


        return external_links

    def read_documents(self, links):
        document_text = []

        return document_text

    def extract_metadata(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.get_text() if soup.title else ""
        meta_description = ""
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag:
            meta_description = meta_desc_tag['content']
        meta_keywords = ""
        meta_keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords_tag:
            meta_keywords = meta_keywords_tag['content']
        metadata = {
            'title': title,
            'description': meta_description,
            'keywords': meta_keywords
            # Add more metadata fields as needed
        }
        return metadata 

    def merge_hyphenated_words(self, text: str) -> str:
        """Merge words in the text that have been split with a hyphen."""
        return re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    def fix_newlines(self, text: str) -> str:
        """Replace single newline characters in the text with spaces."""
        return re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    def remove_multiple_newlines(self, text: str) -> str:
        """Reduce multiple newline characters in the text to a single newline."""
        return re.sub(r"\n{2,}", "\n", text)


    def run_bot(self,depth,follow_external, follow_internal):
        external_links = []
        internal_links = []
        if follow_internal:
            internal_links =  self.get_internal_links(self.url,self.depth)
        if follow_external:
            external_links =  self.get_external_links(self.url,self.depth)
        if not follow_external and not follow_internal:
            self.scrape_page(self.url)

        # if self.read_documents_flag:
        #     all_links = self.external_links + self.internal_links
        #     self.document_text = self.read_documents(all_links)
        
        clean_text = self.remove_multiple_newlines(" ".join(self.text_content))
        clean_text = self.fix_newlines( clean_text)
        clean_text = self.merge_hyphenated_words( clean_text) 

        return clean_text, external_links,internal_links

if __name__ == "__main__":
    url = "http://127.0.0.1:8000/"  
    depth =  1  
    read_documents_flag = 'no' 
    follow_external=True
    follow_internal=True

    bot = WebScraperBot(url, depth, read_documents_flag)
    result = bot.run_bot(depth,follow_external, follow_internal)
    text_content,external_links, internal_links = result 

    # if read_documents_flag:
    #     document_text = result[3]
    #     print("Document text:")
    #     for doc_text in document_text:
    #         print(doc_text)
