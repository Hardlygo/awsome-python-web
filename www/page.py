'''
Author: your name
Date: 2021-01-11 10:07:14
LastEditTime: 2021-01-13 10:20:31
LastEditors: Please set LastEditors
Description: 分页类
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\page.py
'''


class Page(object):
    '''
    Page object for display pages.
    分页类，传入记录总数，当前页，每页大小，构造分页类，包含是否还有下一页，上一页，以及前面有多少个记录

    Page:
        item_count
        page_index
        page_count
        page_size
        page_offset
        page_limit #还剩下多少个元素
        page_has_next #后面还有元素吗
        page_has_previous #前面有元素吗
    '''

    def __init__(self, item_count, page_index=1, page_size=10):
        self.item_count = item_count
        self.page_size = page_size
        self.page_count = item_count//page_size + (1 if item_count % page_size > 0 else 0)

        if item_count == 0 or (page_index > self.page_count):
            self.page_limit = 0
            self.page_offset = 0
            self.page_index = 1
        else:
            self.page_index = page_index
            self.page_limit = self.page_size  # limit和size是一样的
            self.page_offset = (self.page_index-1)*self.page_size

        self.has_next = self.page_index < self.page_count
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__    