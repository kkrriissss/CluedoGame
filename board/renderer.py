import matplotlib
matplotlib.use("TkAgg")


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


COLORMAP = {
    '#': (0.0, 0.0, 0.0),
    'X': (0.0, 1.0, 0.0),
    '1': (0.812, 0.388, 0.388),
    '2': (0.337, 0.118, 0.471),
    '3': (0.682, 0.8, 0.89),
    '4': (0.878, 0.839, 0.153),
    'Q': (0.169, 0.024, 0.024),
    '5': (0.8, 0.671, 0.82),
    '6': (1.0, 0.6, 0.0),
    '7': (0.69, 0.157, 0.157),
    '8': (0.365, 0.549, 0.349),
    '9': (0.4, 0.4, 0.4),
    '%': (0.0, 1.0, 1.0),
    '&': (1.0, 0.0, 1.0),
}

HALLLIGHT = (0.93, 0.93, 0.93)
HALLDARK  = (0.85, 0.85, 0.85)
PLAYERTOKENS = {'S', 'M', 'W', 'G', 'P', 'L'}



def visualize_board(board):
    rows = len(board)
    cols = len(board[0])
    img = np.zeros((rows, cols, 3))

    for r in range(rows):
        for c in range(cols):
            tile = board[r][c]

            if tile == '.':
                img[r, c] = HALLLIGHT if (r + c) % 2 == 0 else HALLDARK
            elif tile in PLAYERTOKENS:
                img[r, c] = (0.2, 0.2, 0.2)
            else:
                img[r, c] = COLORMAP.get(tile, (1.0, 1.0, 1.0))


    fig, ax = plt.subplots(1, 2, figsize=(12, 8), gridspec_kw={'width_ratios': [4, 1]})

    ax[0].imshow(img, interpolation='nearest')
    ax[0].set_title("Cluedo Board Visualization", fontsize=16)
    ax[0].axis('off')

    for r in range(rows):
        for c in range(cols):
            tile = board[r][c]
            if tile in PLAYERTOKENS:
                ax[0].text(
                    c, r, tile,
                    ha='center', va='center',
                    color='white', fontsize=12, fontweight='bold'
                )

    legend_patches = [
        Patch(facecolor=COLORMAP['1'], label="Kitchen"),
        Patch(facecolor=COLORMAP['2'], label="Ballroom"),
        Patch(facecolor=COLORMAP['3'], label="Conservatory"),
        Patch(facecolor=COLORMAP['4'], label="Dining Room"),
        Patch(facecolor=COLORMAP['5'], label="Billiard Room"),
        Patch(facecolor=COLORMAP['6'], label="Library"),
        Patch(facecolor=COLORMAP['7'], label="Lounge"),
        Patch(facecolor=COLORMAP['8'], label="Hall"),
        Patch(facecolor=COLORMAP['9'], label="Study"),
        Patch(facecolor=COLORMAP['Q'], label="Center"),
        Patch(facecolor=COLORMAP['X'], label="Door"),
        Patch(facecolor=COLORMAP['%'], label="Secret Passage"),
        Patch(facecolor=COLORMAP['&'], label="Secret Passage"),
        Patch(facecolor=HALLLIGHT, label="Hallway"),
        Patch(facecolor=COLORMAP['#'], label="Wall")
    ]

    ax[1].legend(handles=legend_patches, loc='center left', fontsize=10)
    ax[1].axis('off')

    plt.tight_layout()
    plt.show(block=True)

