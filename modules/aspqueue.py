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
    __id_counter = 0
    __items_waiting = []
    __items_completed = []
    __items_processing = []
    __lock_get = None
    __lock_processing = None

    def __init__(self, initial_list=[]):
        self.__lock_get = threading.Lock()
        self.__lock_processing = threading.Lock()

        self.__load_workload(initial_list)

    def get_item_to_process(self):
        '''
            Gets an item to be processed from the waiting queue.
        
            :param: none.
        
            :returns: an Item object.
        '''

        with self.__lock_get:
            item = None

            try:
                item = self.__items_waiting.pop()
                self.__items_processing.append(item)
            except IndexError:
                return None

            return item

    def __load_workload(self, initial_list):
        '''
            Loads the queue workload from a given list.
            :param: initial_list
                a list of items to be pushed into the queue            
            :returns: a boolean indicating whether the list was successfully loaded or not
        '''

        if len(initial_list) < 1:
            return False

        for content in initial_list:
            self.push_item(content)

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
        '''
            Removes an item from the processing queue and adds it to the
            completed items list

            :param: item
                item to be marked as completed

            :returns:
                a boolean that indicates if the item was successfully 
                market as completed
        '''

        with self.__lock_processing:
            item, index = self.get_processing_item(item.get_id())

            if item == None:
                return False

            self.__items_processing.pop(index)
            self.__items_completed.append(item)

            return True
    
    def rewind_item(self, item):
        '''
            Removes an item from the processing queue and pushs it back to the
            waiting queue

            :param: item
                item to be rewinded

            :returns: a boolean that indicates if the item was successfully rewinded
        '''

        with self.__lock_processing:
            item, index = self.get_processing_item(item.get_id())

            if item == None:
                return False

            self.__items_processing.pop(index)
            self.__items_waiting.append(item)

            return True

    def get_progress(self):
        '''
            :param: none
            :returns: 
                a percentage corresponding to the ratio between the completed and
                total queue items
        '''

        total_items = len(self.__items_completed) + len(self.__items_processing) + len(self.__items_waiting)

        try:
            return 100 * len(self.__items_completed) / total_items
        except ZeroDivisionError:
            return 0

    def get_completed_counter(self):
        '''
            :param: none
            :returns: the number of completed items
        '''

        return len(self.__items_completed)

    def push_item(self, content):
        '''
            Pushs a item to the queue.
            :param: content
                item content to be pushed into the queue
            :returns: nothing
        '''

        self.__items_waiting.append(Item(self.__id_counter, content))
        self.__id_counter += 1

    def get_waiting_items_counter(self):
        '''
            Returns the number of items waiting to be processed
        '''

        return len(self.__items_waiting)

    def get_total_items_counter(self):
        '''
            Returns the number of items on the queue
        '''

        total_items = len(self.__items_completed) + len(self.__items_processing) + len(self.__items_waiting)
        return total_items
