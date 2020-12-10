from bs4 import BeautifulSoup
with open('index.html',mode='r')as html_doc:
    soup = BeautifulSoup(html_doc, 'html.parser')
    x = soup.get_text()
    print(len(x))
    print(type(x))
    print(x)
    

    
