import os
import tempfile
import shutil
import math
import imageio
import matplotlib.pyplot as plt
import multiprocessing as mp
from matplotlib.figure import Figure
from typing import Callable, Iterable


__version__ = 1.1


def __worker_fn(chunk: Iterable, where: str, fig_fn: Callable[[int], Figure]) -> None:
    try:
        for val in chunk:
            fig = fig_fn(val)
            fig.savefig(os.path.join(where, f'{val}.png'))
            plt.close(fig)
    except KeyboardInterrupt:
        return


def make_gif(
        fig_fn: Callable[[int], Figure],
        num_calls: int,
        filename: str,
        num_processes: int = None,
        show_progress: bool = False,
        writer_kwargs: dict = dict()
) -> None:
    """
    Create a gif by saving figures as .png to a temp directory and then joining them.
    :param fig_fn: The function that will be called to get Figure>
    :param num_calls: The number of calls to the Figure function.
    :param filename: The output filename of the created gif.
    :param num_processes: The number of processes to use. If not set, defaults to number of cores on the CPU.
    :param show_progress: Set to true if you want to show progress via tqdm.
    :param writer_kwargs: Keyword arguments to use inside the imageio writer.
    """
    if num_processes is None:
        num_processes = mp.cpu_count()

    if show_progress:
        # Find out if we are in jupyter notebook or not
        try:
            get_ipython()
            from tqdm.notebook import tqdm
        except NameError:
            from tqdm import tqdm

    calls_arr = list(range(num_calls))
    chunk_size = math.ceil(len(calls_arr) / num_processes)
    chunks = []
    for i in range(num_processes):
        a = chunk_size * i
        b = chunk_size * (i + 1)
        chunks.append(calls_arr[a:b])

    if show_progress:
        calls_arr_pbar = tqdm(calls_arr, desc='Collecting results and creating a gif')
    else:
        calls_arr_pbar = calls_arr

    pool = mp.Pool(num_processes)
    try:
        where = tempfile.mkdtemp()
        pool.starmap(__worker_fn, [(c, where, fig_fn) for c in chunks])
        pool.close()
        pool.join()

        with imageio.get_writer(filename, mode='I', **writer_kwargs) as writer:
            for val in calls_arr_pbar:
                image = imageio.imread(os.path.join(where, f'{val}.png'))
                writer.append_data(image)
    except KeyboardInterrupt as e:
        raise e
    finally:
        pool.close()
        pool.join()

        try:
            shutil.rmtree(where)
        except FileNotFoundError:
            pass
