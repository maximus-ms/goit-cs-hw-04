import logging
import time
from abc import ABC, abstractmethod
from threading import Thread, Lock as ThreadLock
from multiprocessing import Process, Queue
from queue import Empty


class SearcherBase(ABC):
    """
    Abstract class representing a searcher that searches for key words in files.
    """

    def __init__(self, files, key_words):
        """
        Initializes a new instance of the class with the given files and key words.

        :param files: A list of file names.
        :type files: List[str]
        :param key_words: A list of key words to search for in the files.
        :type key_words: List[str]
        :return: None
        """
        self.files = files
        self.key_words = key_words
        self.results = list()
        self.time = 0

    def search_words(self, file_name, key_words, extra_arg=None):
        """
        Searches for the given key words in the specified file.

        Args:
            file_name (str): The name of the file to search in.
            key_words (List[str]): The list of key words to search for.
            extra_arg (Any, optional): An optional extra argument. Defaults to None.

        Raises:
            FileNotFoundError: If the specified file is not found.

        This function opens the specified file in read mode and searches for the given key words in each line of the file. If a key word is found in a line, the corresponding tuple (word, file_name, line_number) is pushed to the results list.
        """
        try:
            with open(file_name, "r") as f:
                for i, line in enumerate(f):
                    line = line.lower()
                    for word in key_words:
                        if word in line:
                            self.push_results((word, file_name, i), extra_arg)
        except FileNotFoundError:
            logging.error(f"File {file_name} not found")

    def worker(self, files, key_words, extra_arg=None):
        """
        Executes the search_words function for each file in the given list of files.

        Args:
            files (List[str]): A list of file names.
            key_words (List[str]): A list of key words to search for in the files.
            extra_arg (Any, optional): An optional extra argument. Defaults to None.

        Raises:
            Exception: If an error occurs during the execution of the search_words function.

        This function iterates over each file in the given list of files and calls the search_words function with the file name, key words, and optional extra argument. If an error occurs during the execution of the search_words function, an error message is logged.
        """
        try:
            for fname in files:
                self.search_words(fname, key_words, extra_arg)
        except Exception as err:
            logging.error(f"Worker error: {err}")

    def search(self, n_workers=1):
        """
        Initiates the search process using the specified number of workers.

        :param n_workers: The number of workers for parallel processing. Defaults to 1.
        :return: The instance of the SearcherBase class.
        """
        _time_ = time.time()
        self.start_workers(n_workers)
        self.time = time.time() - _time_
        self.results.sort()
        return self

    def print_results(self, detailed=False):
        """
        Prints the results of the search operation.

        :param detailed: Whether to print detailed information about each found word. Defaults to False.
        :return: None
        """
        logging.info(f"{self.__class__.__name__} time: {round(self.time, 4)}")
        logging.info(f"Total number of found words: {len(self.results)}")
        if detailed:
            for kword, file_name, line_number in self.results:
                logging.info(f"'{kword}' found in {file_name}[{line_number}]")

    @abstractmethod
    def start_workers(self, n_workers=1):
        """
        Starts a specified number of worker threads or processes to perform a search operation.

        Args:
            n_workers (int, optional): The number of worker threads or processes to start. Defaults to 1.

        Returns:
            None
        """
        pass

    @abstractmethod
    def push_results(self, data, extra_arg=None):
        """
        A method that is meant to be overridden by subclasses to push the results of a search operation.

        :param data: The data to be pushed.
        :type data: Any
        :param extra_arg: An optional extra argument.
        :type extra_arg: Any, optional
        :return: None
        """
        pass


class SingleThreadSearcher(SearcherBase):
    """
    Class representing a searcher that searches for key words in files using a single thread.
    """

    def start_workers(self, n_workers=1):
        """
        Executes the worker function to start the search process using the specified number of workers.

        :param n_workers: The number of worker threads or processes to start. Defaults to 1.
        :type n_workers: int, optional
        :return: None
        """
        self.worker(self.files, self.key_words)

    def push_results(self, data, extra_arg=None):
        """
        Pushes the given data to the results list.

        :param data: The data to be pushed.
        :type data: Any
        :param extra_arg: An optional extra argument.
        :type extra_arg: Any, optional
        :return: None
        """
        self.results.append(data)


class MultiThreadSearcher(SearcherBase):
    """
    Class representing a searcher that searches for key words in files using multiple threads.
    """

    def start_workers(self, n_workers=1):
        """
        Starts a specified number of worker threads to perform a search operation.

        Args:
            n_workers (int, optional): The number of worker threads to start. Defaults to 1.

        Returns:
            None

        This function creates a specified number of worker threads and distributes the files to be searched among them. Each thread is given a portion of the files to search and the key words to search for. The threads are then started and joined to ensure all threads have completed their work before the function returns.
        """
        self.locker = ThreadLock()
        threads = []
        files_per_worker = (len(self.files) + n_workers - 1) // n_workers
        for i in range(n_workers):
            t = Thread(
                target=self.worker,
                args=(
                    self.files[
                        i * files_per_worker : (i + 1) * files_per_worker
                    ],
                    self.key_words,
                ),
            )
            t.start()
            threads.append(t)
        [t.join() for t in threads]

    def push_results(self, data, extra_arg=None):
        """
        Pushes the given data to the results list.

        Args:
            data (Any): The data to be pushed.
            extra_arg (Any, optional): An optional extra argument. Defaults to None.

        Returns:
            None

        This function appends the given data to the `results` list in a thread-safe manner. It uses a lock to ensure that only one thread can access the list at a time.
        """
        with self.locker:
            self.results.append(data)


class MultiProcessSearcher(SearcherBase):
    """
    Class representing a searcher that searches for key words in files using multiple processes.
    Each process is given a portion of the files to search.
    """

    def start_workers(self, n_workers=1):
        """
        Starts a specified number of worker processes to perform a search operation.

        Args:
            n_workers (int, optional): The number of worker processes to start. Defaults to 1.

        Returns:
            None

        This function creates multiple worker processes to distribute the files for searching. Each process is given a subset of files to search and the key words to look for. The processes are started concurrently, and the function waits for all processes to finish before completing.
        """
        processes = []
        queue = Queue()
        files_per_worker = (len(self.files) + n_workers - 1) // n_workers
        for i in range(n_workers):
            p = Process(
                target=self.worker,
                args=(
                    self.files[
                        i * files_per_worker : (i + 1) * files_per_worker
                    ],
                    self.key_words,
                    queue,
                ),
            )
            p.start()
            processes.append(p)
        while any(p.is_alive() for p in processes):
            if not queue.empty():
                self.results.append(queue.get())
        while not queue.empty():
            self.results.append(queue.get())

    def push_results(self, data, queue: Queue):
        """
        Pushes the given data to the specified queue.

        Args:
            data: The data to be pushed.
            queue: The queue to which the data will be pushed.

        Returns:
            None
        """
        queue.put(data)


class MultiProcessSearcher2(MultiProcessSearcher):
    """
    Class representing a searcher that searches for key words in files using multiple processes.
    Each process is taking files to search in from a queue.
    """

    def worker(self, files, key_words, extra_arg=None):
        """
        Executes the search_words function for each file in the given list of files.

        Args:
            files: The queue of file names.
            key_words: The list of key words to search for in the files.
            extra_arg: An optional extra argument. Defaults to None.

        Returns:
            None

        This function takes the next file from the queue until it is not empty. If an error occurs during the execution of the search_words function, an error message is logged.
        """
        try:
            while True:
                self.search_words(files.get(block=False), key_words, extra_arg)
        except Empty:
            pass
        except Exception as err:
            logging.error(f"Worker error: {err}")

    def start_workers(self, n_workers=1):
        """
        Initiates the search process using the specified number of workers.
        :param n_workers: The number of workers for parallel processing. Defaults to 1.
        """
        processes = []
        files_queue = Queue()
        queue = Queue()
        for f in self.files:
            files_queue.put(f)
        for _ in range(n_workers):
            p = Process(
                target=self.worker, args=(files_queue, self.key_words, queue)
            )
            p.start()
            processes.append(p)
        while any(p.is_alive() for p in processes):
            if not queue.empty():
                self.results.append(queue.get())
        while not queue.empty():
            self.results.append(queue.get())


def main():
    from prepare_data import prepare_data

    files_number = 4
    file_name_pattern = "BASIC_data_{}.txt"
    key_words_file_name = "BASIC_key_words.txt"
    prepare_data(file_name_pattern, key_words_file_name, files_number, 20)
    with open(key_words_file_name, "r") as kwords_f:
        key_words = kwords_f.read().split()
    files = [file_name_pattern.format(i) for i in range(files_number)]

    multi_thread_searcher = MultiThreadSearcher(files, key_words)
    multi_thread_searcher.search(n_workers=files_number // 2)
    multi_thread_searcher.print_results(detailed=False)
    multi_process_searcher = MultiProcessSearcher(files, key_words)
    multi_process_searcher.search(n_workers=files_number // 2)
    multi_process_searcher.print_results(detailed=False)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
