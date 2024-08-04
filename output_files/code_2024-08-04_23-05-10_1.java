import java.util.Scanner;

public class Calculator {

    // Функция для вычисления синуса
    public static double calculateSin(double angle) {
        return Math.sin(angle);
    }

    // Функция для вычисления косинуса
    public static double calculateCos(double angle) {
        return Math.cos(angle);
    }

    // Функция для вычисления тангенса
    public static double calculateTan(double angle) {
        return Math.tan(angle);
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        System.out.print("Enter an operator (+, -, *, /, s (sin), c (cos), t (tan)): ");
        char op = scanner.next().charAt(0);

        if (op == 's') {
            System.out.print("Enter angle in radians: ");
            double angle = scanner.nextDouble();
            System.out.printf("sin(%f) = %f\n", angle, calculateSin(angle));
        } else if (op == 'c') {
            System.out.print("Enter angle in radians: ");
            double angle = scanner.nextDouble();
            System.out.printf("cos(%f) = %f\n", angle, calculateCos(angle));
        } else if (op == 't') {
            System.out.print("Enter angle in radians: ");
            double angle = scanner.nextDouble();
            System.out.printf("tan(%f) = %f\n", angle, calculateTan(angle));
        } else {
            System.out.print("Enter two operands:\n");
            double num1 = scanner.nextDouble();
            double num2 = scanner.nextDouble();

            switch (op) {
                case '+':
                    System.out.printf("%f + %f = %f\n", num1, num2, num1 + num2);
                    break;
                case '-':
                    System.out.printf("%f - %f = %f\n", num1, num2, num1 - num2);
                    break;
                case '*':
                    System.out.printf("%f * %f = %f\n", num1, num2, num1 * num2);
                    break;
                case '/':
                    if (num2 != 0) {
                        System.out.printf("%f / %f = %f\n", num1, num2, num1 / num2);
                    } else {
                        System.out.println("Error: Division by zero");
                    }
                    break;
                default:
                    System.out.println("Error: Invalid operator");
                    break;
            }
        }

        scanner.close();
    }
}
