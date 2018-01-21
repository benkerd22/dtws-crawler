import os.path
import crawler
import show

def main():
    src = 'data.txt'
    if not os.path.exists(src):
        with open(src, 'w') as f:
            f.write('{}')
    
    crawler.work(src, only_lastest=False)
    show.show(src, 'result.txt')

if __name__ == '__main__':
    main()