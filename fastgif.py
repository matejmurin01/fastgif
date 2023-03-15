import os
import tempfile
import shutil
import math
import imageio
import matplotlib.pyplot as plt
import multiprocessing as mp
from matplotlib.figure import Figure
from typing import Callable, Iterable, List, Dict, Tuple, Any

__version__ = 2.0


class PreparedOutput:
    def __init__(self,
                 data: Any,
                 title: str = None,
                 title_fontsize: int = 10,
                 x_label: str = None,
                 x_label_fontsize: int = 10,
                 y_label: str = None,
                 y_label_fontsize: int = 10,
                 x_ticks: list = None,
                 x_ticks_fontsize: int = 10,
                 y_ticks: list = None,
                 y_ticks_fontsize: int = 10):
        self.data = data
        self.title = title
        self.title_fontsize = title_fontsize
        self.x_label = x_label
        self.x_label_fontsize = x_label_fontsize
        self.y_label = y_label
        self.y_label_fontsize = y_label_fontsize
        self.x_ticks = x_ticks
        self.x_ticks_fontsize = x_ticks_fontsize
        self.y_ticks = y_ticks
        self.y_ticks_fontsize = y_ticks_fontsize


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


def swapping_gif(data: List[Dict[Tuple[int, int], PreparedOutput]],
                 filename: str,
                 n_rows: int,
                 n_cols: int,
                 num_processes: int = 1,
                 suptitles: List[str] = None,
                 suptitle_fontsize: int = 10,
                 show_progress: bool = False,
                 tight_layout: bool = False,
                 figure_kwargs: dict = None,
                 plot_kwargs: dict = None,
                 writer_kwargs: dict = None):
    if figure_kwargs is None:
        figure_kwargs = {
            'figsize': (10, 10),
            'dpi': 150,
            'facecolor': 'white'
        }
    if plot_kwargs is None:
        plot_kwargs = {
            'vmin': 0,
            'vmax': 1,
            'cmap': plt.cm.nipy_spectral
        }
    global gif_fn

    def gif_fn(idx):
        fig, ax = plt.subplots(n_rows, n_cols, **figure_kwargs)

        for row in range(n_rows):
            for col in range(n_cols):
                plot_data = data[idx][(row, col)]
                ax[row, col].imshow(plot_data.data, **plot_kwargs)
                if plot_data.title is not None:
                    ax[row, col].set_title(plot_data.title, fontsize=plot_data.title_fontsize)
                if plot_data.x_label is not None:
                    ax[row, col].set_xlabel(plot_data.x_label, fontsize=plot_data.x_label_fontsize)
                if plot_data.y_label is not None:
                    ax[row, col].set_ylabel(plot_data.y_label, fontsize=plot_data.y_label_fontsize)
                if plot_data.x_ticks is not None:
                    ax[row, col].set_xticks(plot_data.x_ticks, fontsize=plot_data.x_ticks_fontsize)
                if plot_data.y_ticks is not None:
                    ax[row, col].set_yticks(plot_data.y_ticks, fontsize=plot_data.y_ticks_fontsize)

        if suptitles is not None:
            fig.suptitle(suptitles[idx], fontsize=suptitle_fontsize)

        if tight_layout:
            fig.tight_layout()

        return fig

    make_gif(gif_fn, len(data), filename, num_processes, show_progress=show_progress,
             writer_kwargs=writer_kwargs)


def moving_gif(data: Dict[Tuple[int, int], PreparedOutput],
               filename: str,
               n_rows: int,
               n_cols: int,
               num_steps: int,
               num_processes: int = 1,
               timestamps: List[str] = None,
               suptitles: List[str] = None,
               suptitle_fontsize: int = 10,
               show_progress: bool = False,
               tight_layout: bool = False,
               figure_kwargs: dict = None,
               plot_kwargs: dict = None,
               writer_kwargs: dict = None):
    if figure_kwargs is None:
        figure_kwargs = {
            'figsize': (10, 10),
            'dpi': 150,
            'facecolor': 'white'
        }
    if plot_kwargs is None:
        plot_kwargs = {
            'vmin': 0,
            'vmax': 1,
            'cmap': plt.cm.nipy_spectral
        }
    global gif_fn

    def gif_fn(idx):
        fig, ax = plt.subplots(n_rows, n_cols, **figure_kwargs)

        for row in range(n_rows):
            for col in range(n_cols):
                if (row, col) not in data:
                    continue
                plot_data = data[(row, col)]
                ax[row, col].imshow(plot_data.data[idx], **plot_kwargs)
                if timestamps is not None:
                    tstep_txt = ' ' + timestamps[idx]
                else:
                    tstep_txt = ''

                if plot_data.title is not None:
                    ax[row, col].set_title(plot_data.title + tstep_txt, fontsize=plot_data.title_fontsize)
                if plot_data.x_label is not None:
                    ax[row, col].set_xlabel(plot_data.x_label, fontsize=plot_data.x_label_fontsize)
                if plot_data.y_label is not None:
                    ax[row, col].set_ylabel(plot_data.y_label, fontsize=plot_data.y_label_fontsize)
                if plot_data.x_ticks is not None:
                    ax[row, col].set_xticks(plot_data.x_ticks, fontsize=plot_data.x_ticks_fontsize)
                if plot_data.y_ticks is not None:
                    ax[row, col].set_yticks(plot_data.y_ticks, fontsize=plot_data.y_ticks_fontsize)

        if suptitles is not None:
            fig.suptitle(suptitles[idx], fontsize=suptitle_fontsize)

        if tight_layout:
            fig.tight_layout()

        return fig

    make_gif(gif_fn, num_steps, filename, num_processes, show_progress=show_progress, writer_kwargs=writer_kwargs)
