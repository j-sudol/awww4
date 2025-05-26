const boardContainer = document.getElementById("board_container") as HTMLDivElement;
const raw = document.getElementById("board_input") as HTMLInputElement;
const saveGameButton = document.getElementById("save-button") as HTMLButtonElement;
const saveDotsInput = document.getElementById("save-dots") as HTMLInputElement;
const gameDotsInput = document.getElementById("game_dots_input") as HTMLInputElement;

interface Board {
    name: string;
    columns: number;
    rows: number;
    dots: {
        row: number;
        col: number;
        color: string;
    }[];
}

interface Dot {
    row: number;
    col: number;
    color: string;
}

const board: Board = JSON.parse(raw.value);
const cols = board.columns;
const rows = board.rows;
const dots: Dot[] = board.dots;

let isDrawing = false;
let pathCompleted = false;
let currentColor = "";
let currentPath: { cell: HTMLElement, row: number, col: number }[] = [];
let startDotCell: HTMLElement | null = null;

function RGBToHex(rgb: string): string {
    const result = /^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/.exec(rgb);
    if (!result) return "";
    const [, r, g, b] = result;
    const toHex = (x: number) => (x < 16 ? "0" : "") + x.toString(16);
    return "#" + toHex(parseInt(r)).toUpperCase() + toHex(parseInt(g)).toUpperCase() + toHex(parseInt(b)).toUpperCase();
}

function removeOldPathOfColor(color: string) {
    for (let i = dots.length - 1; i >= 0; i--) {
        const dot = dots[i];
        const index = dot.row * cols + dot.col;
        const cell = boardContainer.children[index] as HTMLElement;
        if (dot.color.toUpperCase() === color && cell && !cell.style.border) {
            cell.style.backgroundColor = "";
            dots.splice(i, 1);
        }
    }
}

function cancelCurrentPath() {
    currentPath.forEach(({ cell, row, col }) => {
        if (cell !== startDotCell) {
            const index = dots.findIndex(dot => dot.row === row && dot.col === col && !cell.style.border);
            if (index !== -1) dots.splice(index, 1);
            cell.style.backgroundColor = "";
        }
    });
    currentPath = [];
    isDrawing = false;
    pathCompleted = false;
    startDotCell = null;
    boardContainer.classList.remove("drawing");
}

function paintCell(cell: HTMLElement, row: number, col: number) {
    if (cell === startDotCell) {
        return;
    }

    if (!cell.style.border) {
        const hex = RGBToHex(cell.style.backgroundColor).toUpperCase();
        if (hex && hex !== currentColor) {
            cancelCurrentPath();
            return;
        }

        cell.style.backgroundColor = currentColor;
        const existingIndex = dots.findIndex(dot => dot.row === row && dot.col === col);
        if (existingIndex !== -1) {
            dots[existingIndex].color = currentColor;
        } else {
            dots.push({ row, col, color: currentColor });
        }
        currentPath.push({ cell, row, col });

    } else {
        const hex = RGBToHex(cell.style.backgroundColor).toUpperCase();
        if (hex && hex !== currentColor) {
            cancelCurrentPath();
            return;
        }

        if (hex === currentColor && currentPath.length > 0) {
            const startDot = currentPath[0].cell;

            if (startDot !== cell) {
                startDot.style.border = "2px solid green";
                cell.style.border = "2px solid green";
                pathCompleted = true;
            }

            isDrawing = false;
            currentPath = [];
            startDotCell = null;
            boardContainer.classList.remove("drawing");
        }
    }
}

function create_board() {
    boardContainer.innerHTML = "";
    boardContainer.style.gridTemplateRows = `repeat(${rows}, 1fr)`;
    boardContainer.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            const cell = document.createElement("div");
            cell.className = "grid-cell";

            cell.addEventListener("mousedown", () => {
                if (cell.style.border) {
                    const bg = window.getComputedStyle(cell).backgroundColor;
                    const hex = RGBToHex(bg);
                    if (!hex) return;

                    currentColor = hex.toUpperCase();

                    // Reset borders of dots of that color
                    dots.forEach(dot => {
                        if (dot.color.toUpperCase() === currentColor) {
                            const index = dot.row * cols + dot.col;
                            const cell = boardContainer.children[index] as HTMLElement;
                            if (cell && cell.style.border) {
                                cell.style.border = "2px solid #000";
                            }
                        }
                    });

                    removeOldPathOfColor(currentColor);

                    isDrawing = true;
                    pathCompleted = false;
                    currentPath = [{ cell, row: i, col: j }];
                    startDotCell = cell;

                    boardContainer.classList.add("drawing");
                }
            });

            cell.addEventListener("mouseenter", () => {
                if (isDrawing) {
                    paintCell(cell, i, j);
                }
            });

            boardContainer.appendChild(cell);
        }
    }

    document.addEventListener("mouseup", () => {
        if (isDrawing && !pathCompleted) {
            cancelCurrentPath();
        }

        isDrawing = false;
        pathCompleted = false;
        currentPath = [];
        startDotCell = null;
        boardContainer.classList.remove("drawing");
    });

    // Apply predefined start dots
    dots.forEach(dot => {
        const index = dot.row * cols + dot.col;
        const cell = boardContainer.children[index] as HTMLElement;
        if (cell) {
            cell.style.backgroundColor = dot.color;
            cell.style.border = "2px solid #000";
        }
    });

    const gameDots = JSON.parse(gameDotsInput.value);
    gameDots.forEach((gameDot: Dot) => {
        const index = gameDot.row * cols + gameDot.col;
        const cell = boardContainer.children[index] as HTMLElement;
        if (cell && !cell.style.border) {
            cell.style.backgroundColor = gameDot.color;
            const existingDotIndex = dots.findIndex(dot => dot.row === gameDot.row && dot.col === gameDot.col);
            if (existingDotIndex !== -1) {
                dots[existingDotIndex].color = gameDot.color;
            } else {
                dots.push({ row: gameDot.row, col: gameDot.col, color: gameDot.color });
            }
        }
    });
}

window.addEventListener("DOMContentLoaded", () => {
    create_board();
});

saveGameButton.addEventListener("click", () => {
    const dotsToSave = dots.map(dot => ({
        row: dot.row,
        col: dot.col,
        color: dot.color
    }));
    saveDotsInput.value = JSON.stringify(dotsToSave);
    (saveGameButton.closest("form") as HTMLFormElement).submit();
});
