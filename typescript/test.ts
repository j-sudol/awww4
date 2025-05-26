// Definiujemy zmienną z typem string
let greeting: string = "Cześć, TypeScript!";

// Funkcja, która przyjmuje imię i zwraca powitanie
function sayHello(name: string): string {
  return `${greeting} Witaj, ${name}!`;
}

// Wywołanie funkcji i wyświetlenie wyniku w konsoli
console.log(sayHello("Kuba"));
