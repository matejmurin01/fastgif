# fastgif
Python package for creating a gif utilizing multiprocessing to speed up the process.
The individual plots are saved in a temp directory and are afterwards cleaned.
This takes into account keyboard interrupts as well.

## Usage

```python
import fastgif
import matplotlib.pyplot as plt
import numpy as np


def get_fig(idx):
    x_space = np.linspace(0, 10, 30) + (idx / 20)

    fig, ax = plt.subplots(dpi=150)

    ax.plot(x_space, np.sin(x_space))
    ax.grid()
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('x')
    ax.set_ylabel('sin(x)')
    fig.suptitle(f'Sine wave gif')

    return fig


fastgif.make_gif(get_fig, 100, 'images/sine.gif', show_progress=True, writer_kwargs={'duration': 0.01})
```

Creates the following gif:

![sine.gif](https://github.com/matejmurin01/fastgif/blob/main/images/sine.gif)
