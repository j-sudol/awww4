"use strict";
// Definiujemy zmienną z typem string
let greeting = "Cześć, TypeScript!";
// Funkcja, która przyjmuje imię i zwraca powitanie
function sayHello(name) {
    return `${greeting} Witaj, ${name}!`;
}
// Wywołanie funkcji i wyświetlenie wyniku w konsoli
console.log(sayHello("Kuba"));
