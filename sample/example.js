// Ejemplo de código JavaScript
function calculateFactorial(n) {
    // Validación de entrada
    if (typeof n !== 'number' || n < 0) {
        throw new Error('Input must be a non-negative number');
    }

    // Caso base
    if (n === 0 || n === 1) {
        return 1;
    }

    // Cálculo recursivo
    return n * calculateFactorial(n - 1);
}

// Ejemplo de uso de la función
try {
    const number = 5;
    const result = calculateFactorial(number);
    console.log(`El factorial de ${number} es: ${result}`);
} catch (error) {
    console.error('Error:', error.message);
}

/* 
 * Ejemplo de clase con ES6
 */
class MathOperations {
    constructor() {
        this.pi = 3.14159;
    }

    add(a, b) {
        return a + b;
    }

    subtract(a, b) {
        return a - b;
    }

    multiply(a, b) {
        return a * b;
    }
}