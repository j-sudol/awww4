const gridContainer = document.getElementById("grid-container")!;
const genButton = document.getElementById("generate-button")!;
const saveButton = document.getElementById("save-button")!;
const rowsInput = document.getElementById("rows") as HTMLInputElement;
const colsInput = document.getElementById("columns") as HTMLInputElement;
const colorsInput = document.getElementById("color") as HTMLInputElement;

interface DotData {
    row: number;
    col: number;
    color: string;
}

const dotsInput = document.getElementById("dots-json") as HTMLInputElement;

let colors: {[color: string]: number} = {}
const colorLimit = 2;

genButton.addEventListener("click", () => {
    const rows = parseInt(rowsInput.value);
    const cols = parseInt(colsInput.value);
    if (isNaN(rows) || isNaN(cols) || rows <= 0 || cols <= 0) {
        alert("Please enter valid positive integers for rows and columns.");
        return;
    }
    console.log(`Generating grid with ${rows} rows and ${cols} columns...`);
    generateGrid(rows, cols);
});

function rgbToHex(rgb: string): string {
    const result = /^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/.exec(rgb);
    if (!result) return "";

    const r = parseInt(result[1], 10);
    const g = parseInt(result[2], 10);
    const b = parseInt(result[3], 10);

    const toHex = (x: number) => (x < 16 ? "0" : "") + x.toString(16);

    return "#" + toHex(r) + toHex(g) + toHex(b);
}

let currentrows = 0;
let currentcols = 0;

function generateGrid(rows: number, cols: number, dots: DotData[] = []) {
    if(rows === currentrows && cols === currentcols){
        return; 
    }

    currentcols = cols;
    currentrows = rows;
    
    colors = {};

    gridContainer.innerHTML = ""; // Clear previous grid
    
    gridContainer.style.display = "grid";
    gridContainer.style.gridTemplateRows = `repeat(${rows}, 40px)`;
    gridContainer.style.gridTemplateColumns = `repeat(${cols}, 40px)`;

    for (let i = 0; i < rows * cols; i++) {
        const cell = document.createElement("div");
        cell.className = "grid-cell";
        cell.style.border = "1px solid black";
        cell.style.display = "flex";
        cell.style.alignItems = "center";
        cell.style.justifyContent = "center";
        
        // Add event listener to change color on click
        cell.addEventListener("click", () => {
            const currentColor = document.getElementById("selected-color") as HTMLInputElement;
            const selectedColor = currentColor.value.toUpperCase();

            const previousRgb = cell.style.backgroundColor;
            const previousHex = rgbToHex(previousRgb).toUpperCase();

            if(previousHex === selectedColor){
                cell.style.backgroundColor = "";
                colors[selectedColor]--;
                return;
            }

            if((colors[selectedColor]||0) >= colorLimit ){
                return;
            }

            if(previousHex){
                colors[previousHex]--;
            }

            colors[selectedColor] = (colors[selectedColor] || 0) +1;
            cell.style.backgroundColor = selectedColor;
            console.log(colors);
        });

        gridContainer.appendChild(cell);
    }

    dots.forEach(dot => {
        const index = dot.row * cols + dot.col;
        const cell = gridContainer.children[index] as HTMLElement;
        if (cell) {
            const color = dot.color.toUpperCase()
            cell.style.backgroundColor = color;
            colors[color] = (colors[color] || 0) + 1;
        }
    });

    console.log(colors);
}



function collectBoardData() {
    const cols = parseInt(colsInput.value);
    const rows = parseInt(rowsInput.value);
    const cells = document.querySelectorAll(".grid-cell");
    const dots: {row: number, col: number, color: string}[] = [];

    cells.forEach((cell, index) => {
        const row = Math.floor(index/cols);
        const col = index % cols;
        const color = (cell as HTMLElement).style.backgroundColor;

        if (color && color !== ""){
            const hexColor = rgbToHex(color);
        
            dots.push({row, col, color: hexColor});
        }
    });

    return dots;
}

saveButton.addEventListener("click", () => {
    const dots = collectBoardData();
    const dotsInput = document.getElementById("dots-json") as HTMLInputElement;
    dotsInput.value = JSON.stringify(dots);

    if (dots.length === 0) {
        const confirmEmpty = confirm("Nie zaznaczono żadnych kropek. Czy na pewno zapisać?");
        if (!confirmEmpty) return;
    }

    (saveButton.closest("form") as HTMLFormElement).submit();
});

window.addEventListener("DOMContentLoaded", () => {
    const rows = parseInt(rowsInput.value);
    const cols = parseInt(colsInput.value);
    const dots: DotData[] = JSON.parse(dotsInput.value || "[]");

    if (rows > 0 && cols > 0) {
        generateGrid(rows, cols, dots);
    }
});