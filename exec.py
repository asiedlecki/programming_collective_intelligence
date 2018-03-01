import searchengine
crawler = searchengine.crawler('searchindex.db')
pages = ['http://kiwitobes.com/wiki/Categorical_list_of_programming_languages.html']
crawler.crawl(pages)