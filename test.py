import logging
from prepare_data import prepare_data
from searcher import SingleThreadSearcher, MultiThreadSearcher
from searcher import MultiProcessSearcher, MultiProcessSearcher2


def print_results(searcher, detailed=False):
    """
    Print the results of a searcher.

    Args:
        searcher (SearcherBase): The searcher object containing the results.
        detailed (bool, optional): Whether to print detailed information about each found word. Defaults to False.

    Returns:
        None

    This function prints the time taken by the searcher and the total number of found words. If `detailed` is True,
    it also prints information about each found word, including the keyword, file name, and line number.

    """
    logging.info(
        f"{searcher.__class__.__name__} time: {round(searcher.time, 4)}"
    )
    logging.info(f"Total number of found words: {len(searcher.results)}")
    if detailed:
        for kword, file_name, line_number in searcher.results:
            logging.info(f"'{kword}' found in {file_name}[{line_number}]")


def save_results(fname, results):
    """
    Save the results to a file.

    Parameters:
        fname (str): The name of the file to save the results to.
        results (List[Tuple[str, str, int]]): The results to be saved, where each result is a tuple containing the keyword, file name, and line number.

    Returns:
        None

    This function opens the specified file in write mode and writes the results to the file in the format "keyword file_name line_number". Each result is written on a new line.

    Example:
        save_results("results.txt", [("keyword1", "file1.txt", 10), ("keyword2", "file2.txt", 20)])
        # Results in the file "results.txt" containing:
        # keyword1 file1.txt 10
        # keyword2 file2.txt 20
    """
    with open(fname, "w") as f:
        f.write(
            "\n".join(
                f"{kword} {file_name} {line_number}"
                for kword, file_name, line_number in results
            )
        )


def run_tests(
    files_number,
    lines_number_max,
    n_workers=1,
    test_name="test1",
    generate_data=False,
):
    """
    Run tests for file searcher with different approaches.

    Parameters:
        files_number (int): The number of files to be processed.
        lines_number_max (int): The maximum number of lines in each file.
        n_workers (int, optional): The number of workers for parallel processing. Defaults to 1.
        test_name (str, optional): The name of the test. Defaults to "test1".
        generate_data (bool, optional): Whether to generate data for the test. Defaults to False.

    Returns:
        None

    This function runs tests for the file searcher with different approaches. It generates data for the test if `generate_data` is True. It then performs the following steps:
    1. Prints the test parameters.
    2. Generates the file name pattern and key words file name based on the test name.
    3. Reads the key words from the key words file.
    4. Generates the list of files based on the file name pattern and the number of files.
    5. Performs search using SingleThreadSearcher and prints the results.
    6. Compares the results of SingleThreadSearcher with MultiThreadSearcher. If they are not equal, saves the MultiThreadSearcher results and logs an error.
    7. Compares the results of SingleThreadSearcher with MultiProcessSearcher. If they are not equal, saves the MultiProcessSearcher results and logs an error.
    8. Compares the results of SingleThreadSearcher with MultiProcessSearcher2. If they are not equal, saves the MultiProcessSearcher2 results and logs an error.
    9. Prints the test result as "PASSED" if no errors occurred, otherwise logs "FAILED".
    """
    logging.info(f"Run test {test_name}")
    logging.info(
        f"files_number: {files_number}, lines_number_max: {lines_number_max}, n_workers: {n_workers}"
    )

    file_name_pattern = test_name + "_data_{}.txt"
    key_words_file_name = f"{test_name}_key_words.txt"

    if generate_data:
        prepare_data(
            file_name_pattern,
            key_words_file_name,
            files_number,
            lines_number_max,
        )

    with open(key_words_file_name, "r") as kwords_f:
        key_words = kwords_f.read().split()
    files = [file_name_pattern.format(i) for i in range(files_number)]

    single_thread_searcher = SingleThreadSearcher(files, key_words).search(
        n_workers
    )
    single_thread_searcher.print_results()
    failed = False

    multi_thread_searcher = MultiThreadSearcher(files, key_words).search(
        n_workers
    )
    multi_thread_searcher.print_results()
    if single_thread_searcher.results != multi_thread_searcher.results:
        save_results(
            f"{test_name}_multi_thread_searcher_results.txt",
            multi_thread_searcher.results,
        )
        logging.error(
            "MultiThreadSearcher results are not equal to SingleThreadSearcher results"
        )
        failed = True

    multi_process_searcher = MultiProcessSearcher(files, key_words).search(
        n_workers
    )
    multi_process_searcher.print_results()
    if single_thread_searcher.results != multi_process_searcher.results:
        save_results(
            f"{test_name}_multi_process_searcher_results.txt",
            multi_process_searcher.results,
        )
        logging.error(
            "MultiProcessSearcher results are not equal to SingleThreadSearcher results"
        )
        failed = True

    multi_process_searcher2 = MultiProcessSearcher2(files, key_words).search(
        n_workers
    )
    multi_process_searcher2.print_results()
    if single_thread_searcher.results != multi_process_searcher2.results:
        save_results(
            f"{test_name}_multi_process_searcher2_results.txt",
            multi_process_searcher2.results,
        )
        logging.error(
            "MultiProcessSearcher2 results are not equal to SingleThreadSearcher results"
        )
        failed = True

    if failed:
        save_results(
            f"{test_name}_single_thread_searcher_results.txt",
            single_thread_searcher.results,
        )

    logging.info(
        f"Test '{test_name}': {'PASSED' if not failed else 'FAILED'}\n"
    )


def main():
    run_tests(2, 20, n_workers=1, test_name="BASIC", generate_data=True)
    run_tests(8, 1_000, n_workers=2, test_name="MEDIUM", generate_data=True)
    run_tests(16, 10_000, n_workers=4, test_name="MAX", generate_data=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
