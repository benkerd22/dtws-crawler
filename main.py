import os.path
import crawler
import show

def main():
    src = 'data.txt'
    if not os.path.exists(src):
        with open(src, 'w') as f:
            f.write('{}')
    
    crawler.work(src)
    show.show(src, 'result.txt')

if __name__ == '__main__':
    #crawler.role_crawler(901071496192949, 57)
    main()