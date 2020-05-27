import requests
import threading

class Item:
    __id = None
    __processing_start = 0
    content = None

    def __init__(self, id, content):
        self.__id = id
        self.content = content

    def get_id(self):
        return self.__id

class Queue:
    __items_waiting = []
    __items_completed = []
    __items_processing = []
    __lock_get = None
    __lock_processing = None

    def __init__(self, url):
        self.__load_workload(url)
        self.__lock_get = threading.Lock()
        self.__lock_processing = threading.Lock()

    def get_item_to_process(self):
        """Gets a item from the waiting queue to be processed.
        
        :param: none.
        
        :returns: an Item object.
        """
        with self.__lock_get:
            item = None

            try:
                item = self.__items_waiting.pop()
                self.__items_processing.append(item)
            except IndexError:
                return None

            return item

    def __load_workload(self, url):
        print("Fetching workload...")

        req = requests.get(url)

        id_counter = 0

        for url in req.text.split("\n"):            
            self.__items_waiting.append(Item(id_counter, url))
            id_counter += 1

        print("{} items loaded.".format(len(self.__items_waiting)))
        return True

    def get_processing_item(self, id):
        '''
            Search the processing items queue for an item by id.

            If any item id matches the desired id, this function returns a
            pair with the item object and the index of that item on the processing queue
            of the following format: ItemObject, ItemIndex. 

            If no item matches the id desired, this function will return a pair
            on the following format: None, -1, indicating an invalid pair.
        '''
        for index in range(len(self.__items_processing)):
            item = self.__items_processing[index]

            if (item.get_id() == id):
                return item, index

        return None, -1

    def complete_item(self, item):
        """
        """
        with self.__lock_processing:
            item, index = self.get_processing_item(item.get_id())

            if item == None:
                return False

            self.__items_processing.pop(index)
            self.__items_completed.append(item)

            return True
    
    def rewind_item(self, item):
        with self.__lock_processing:
            item, index = self.get_processing_item(item.get_id())

            if item == None:
                return False

            self.__items_processing.pop(index)
            self.__items_waiting.append(item)

            return True

    def get_progress(self):
        total_items = len(self.__items_completed) + len(self.__items_processing) + len(self.__items_waiting)
        return 100 * len(self.__items_completed) / total_items

    def get_completed_counter(self):
        return len(self.__items_completed)

"""
    #Deprecated
    def check_duplicated_completed(self):
        duplicated = 0
        ids = []
        for item in self.__items_completed:
            if (item.get_id() in ids):
                duplicated += 1

            ids.append(item.get_id())

        print("{} items duplicated. {} items processed.".format(duplicated, len(self.__items_completed)))
"""