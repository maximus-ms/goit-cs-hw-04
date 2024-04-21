# GoITNeo CS HW-04

## Task

Develop a program that simultaneously analyzes text files for the search of specific keywords. Create two versions of the program: one using the `threading` module for multithreading, and another using the `multiprocessing` module for multiprocessing programming.

### Instructions
1. Implement multithreading approach to file processing (using threading):
    - Divide the list of files between different threads.
    - Each thread should search for the specified keywords in its own set of files.
    - Save and print the search results from all threads.

2. Implement multiprocessing approach to file processing (using multiprocessing):
    - Divide the list of files between different processes.
    - Each process should handle its own part of files, searching for the keywords.
    - Use inter-process communication mechanism (e.g., Queue) to collect and print the search results.

#### Solution

Classes of different approaches are implemented in the `searcher.py` file.

##### Classes

* `SingleThreadSearcher`: A searcher that searches for key words in files using a single thread.
* `MultiThreadSearcher`: A searcher that searches for key words in files using multiple threads.
* `MultiProcessSearcher`: A searcher that searches for key words in files using multiple processes.
* `MultiProcessSearcher2`: A searcher that searches for key words in files using multiple processes and file distribution using Queue.


Additional files:
 - `prepare_data.py` - contains functions that prepares data for the test using the `faker` library.
 - `test.py` - runs tests.
