class Page:
    """Wrapper used to contain info about a single page"""

    def __init__(self, index: int) -> None:
        super().__init__()
        self.index_start = index
        self.index_end = index
        self.elements = []
        self.total_elements = 0


class Paginator:
    """Simple class constructed by a list of elements and a page size, and exposes methods to generate pages out of
    it """

    def __init__(self, to_be_paginated: list, page_size: int, inner_list_key='') -> None:
        """
        Paginator constructor
        :param to_be_paginated: the list of elements to be paginated
        :param page_size: the minimum amount of elements that should be inserted in each page. Minimum 1.
        :param inner_list_key: is the element contain the real elements that will be displayed, this optional field contains its key.
        """
        super().__init__()
        self.current_page = 0
        self.pages = []

        new_page = None
        for index, element in enumerate(to_be_paginated):
            # If no page is present, create a new one starting and finishing at current index
            if not new_page:
                new_page = Page(index)

            # Add the current element of the to_be_paginated list to the page currently being built
            new_page.elements.append(element)
            new_page.index_end = index
            new_page.total_elements += len(element[inner_list_key]) if inner_list_key else 1

            # If page is full, or all the elements were processed, close it
            if new_page.total_elements >= page_size or index == len(to_be_paginated) - 1:
                self.pages.append(new_page)
                new_page = None

    def pages_number(self) -> int:
        return len(self.pages)

    def get_page(self, index=None) -> Page:
        return self.pages[index or self.current_page]

    def prev_page(self) -> Page:
        if self.current_page > 0:
            self.current_page -= 1
        return self.get_page()

    def next_page(self) -> Page:
        if self.current_page < self.pages_number() - 1:
            self.current_page += 1
        return self.get_page()
