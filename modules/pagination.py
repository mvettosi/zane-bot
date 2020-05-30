class Paginator:
    """Simple class constructed by a list of elements and a page size, and exposes methods to generate pages out of
    it """

    def __init__(self, to_be_paginated, page_size, inner_list_key=None):
        """
        Paginator constructor
        :param to_be_paginated: the list of elements to be paginated
        :param page_size: the minimum amount of elements that should be inserted in each page. Minimum 1.
        :param inner_list_key: is the element contain the real elements that will be displayed, this optional field contains its key.
        """
        self.current_page = 0
        self.pages = []

        new_page = None
        for index, element in enumerate(to_be_paginated):
            # If no page is present, create a new one starting and finishing at current index
            if not new_page:
                new_page = {'index_start': index, 'index_end': index, 'elements': [], 'total_elements': 0}

            # Add the current element of the to_be_paginated list to the page currently being built
            new_page['elements'].append(element)
            new_page['index_end'] = index
            new_page['total_elements'] += len(element[inner_list_key]) if inner_list_key else 1

            # If page is full, close it
            if new_page['total_elements'] >= page_size:
                self.pages.append(new_page)
                new_page = None

    def pages_number(self):
        return len(self.pages)

    def get_page(self, index=None):
        return self.pages[index or self.current_page]['elements']

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        return self.get_page()

    def next_page(self):
        if self.current_page < self.pages_number() - 1:
            self.current_page += 1
        return self.get_page()
