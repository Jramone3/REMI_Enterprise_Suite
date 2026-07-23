def saludar(nombre):
    """
    Esta función saluda a la persona con el nombre dado.
    """
    return f"¡Hola, {nombre}! ¡Bienvenido!"

if __name__ == "__main__":
    print("¡Este es un ejemplo de código Python!")
    mensaje = saludar("Ramón")
    print(mensaje)
    print("Remi descansa por hoy, tuvimos buena jornada. Mañana volvemos a trabajar.")

    # Un pequeño bucle de ejemplo
    for i in range(3):
        print(f"Contador: {i + 1}")