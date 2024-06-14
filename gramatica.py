# -----------------------------------------------------------------------------
# Rainman Sián
# 07-02-2020
#
# Ejemplo mi primer proyecto con Python utilizando ply en Ubuntu
# -----------------------------------------------------------------------------

tokens  = (
    'REVALUAR',
    'PARIZQ',
    'PARDER',
    'CORIZQ',
    'CORDER',
    'MAS',
    'MENOS',
    'POR',
    'DIVIDIDO',
    'DECIMAL',
    'ENTERO',
    'PTCOMA'
)

# Tokens
t_REVALUAR  = r'Evaluar'
t_PARIZQ    = r'\('
t_PARDER    = r'\)'
t_CORIZQ    = r'\['
t_CORDER    = r'\]'
t_MAS       = r'\+'
t_MENOS     = r'-'
t_POR       = r'\*'
t_DIVIDIDO  = r'/'
t_PTCOMA    = r';'

def t_DECIMAL(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        print("Floaat value too large %d", t.value)
        t.value = 0
    return t

def t_ENTERO(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Caracteres ignorados
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Construyendo el analizador léxico
import ply.lex as lex
lexer = lex.lex()


# Asociación de operadores y precedencia
precedence = (
    ('left','MAS','MENOS'),
    ('left','POR','DIVIDIDO'),
    ('right','UMENOS'),
    )

# Definición de la gramática
def p_instrucciones_lista(t):
    '''instrucciones    : instruccion instrucciones
                        | instruccion '''

def p_instrucciones_evaluar(t):
    'instruccion : REVALUAR CORIZQ expresion CORDER PTCOMA'
    print('El valor de la expresión es: ' + str(t[3]))

def p_expresion_binaria(t):
    '''expresion : expresion MAS expresion
                  | expresion MENOS expresion
                  | expresion POR expresion
                  | expresion DIVIDIDO expresion'''
    if t[2] == '+'  : t[0] = t[1] + t[3]
    elif t[2] == '-': t[0] = t[1] - t[3]
    elif t[2] == '*': t[0] = t[1] * t[3]
    elif t[2] == '/': t[0] = t[1] / t[3]

def p_expresion_unaria(t):
    'expresion : MENOS expresion %prec UMENOS'
    t[0] = -t[2]

def p_expresion_agrupacion(t):
    'expresion : PARIZQ expresion PARDER'
    t[0] = t[2]

def p_expresion_number(t):
    '''expresion    : ENTERO
                    | DECIMAL'''
    t[0] = t[1]

def p_error(t):
    print("Error sintáctico en '%s'" % t.value)

import ply.yacc as yacc
parser = yacc.yacc()


"""
Python calculadora usando Tkinter 
Versión 3
"""

from tkinter import *
from tkinter import messagebox
import ply.yacc as yacc
parser = yacc.yacc()



# variable expression, que luego usaremos globalmente
expression = ""


# Funcion para actualizar el contenido del visor
def press(num):
	global expression
	# concatenar la expresión + el nuemero pasado por parametro
	expression = expression + str(num)
	# actualizar la expresión
	equation.set(expression)


# Funcion para evaluar la expresion final
def equalpress():
    global expression
    parser.parse(str(expression))
"""   try:
        global expression
        # La función eval() se utiliza para evaluar cadenas de
        # texto que pueden contener expresiones o distintos
        # tipos de estructuras de datos que pueden utilizarse con Python
        total = str(eval(expression))
        equation.set(total)
        # Cargar total en la expresión
        expression = total  # Si hay algún error
    except ZeroDivisionError:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message="No se puede dividir por Cero")
    except Exception:
        equation.set("0")
        expression = ""
        messagebox.showerror(title="Error", message="Se produjo un error")
"""

# Function to clear the contents
# of text entry box
def clear():
	global expression
	expression = ""
	equation.set("0")


ventana = Tk()
ventana.title("Calculadora")

# Se configura el ancho y alto con .geometry()
ventana.geometry("265x125")

# Las variables de control son objetos especiales que se asocian a los widgets
#  para almacenar sus valores y facilitar su disponibilidad
# en otras partes del programa.
# Pueden ser de tipo numérico, de cadena y booleano.
equation = StringVar()

# Caja para cargar y ver resultados
visor = Entry(textvariable=equation)
visor.config(state='disabled')
# El metodo grid is usado para posicion los widget con posiciones relativas
# en una  estructura tipo tabla.
visor.grid(columnspan=4, ipadx=70)

equation.set('0')


# Creamos los botones
# Con grid posicionamos.
# Cuando se presionan los botones, se dispara una función
# lambda que ademas llama a otra funcion "press"
button1 = Button(text=' 1 ', fg='black', bg='white',
                 command=lambda: press(1), height=1, width=7)
button1.grid(row=2, column=0)

button2 = Button(text=' 2 ', fg='black', bg='white',
                 command=lambda: press(2), height=1, width=7)
button2.grid(row=2, column=1)

button3 = Button(text=' 3 ', fg='black', bg='white',
                 command=lambda: press(3), height=1, width=7)
button3.grid(row=2, column=2)

button4 = Button(text=' 4 ', fg='black', bg='white',
                 command=lambda: press(4), height=1, width=7)
button4.grid(row=3, column=0)

button5 = Button(text=' 5 ', fg='black', bg='white',
                 command=lambda: press(5), height=1, width=7)
button5.grid(row=3, column=1)


button6 = Button(text=' 6 ', fg='black', bg='white',
                 command=lambda: press(6), height=1, width=7)
button6.grid(row=3, column=2)


button7 = Button(text=' 7 ', fg='black', bg='white',
                 command=lambda: press(7), height=1, width=7)
button7.grid(row=4, column=0)

button8 = Button(text=' 8 ', fg='black', bg='white',
                 command=lambda: press(8), height=1, width=7)
button8.grid(row=4, column=1)

button9 = Button(text=' 9 ', fg='black', bg='white',
                 command=lambda: press(9), height=1, width=7)
button9.grid(row=4, column=2)

button0 = Button(text=' 0 ', fg='black', bg='white',
                 command=lambda: press(0), height=1, width=7)
button0.grid(row=5, column=0)

bsuma = Button(text=' + ', fg='black',
               command=lambda: press("+"), height=1, width=7)
bsuma.grid(row=2, column=3)


bresta = Button(text=' - ', fg='black',
                command=lambda: press("-"), height=1, width=7)
bresta.grid(row=3, column=3)


bmult = Button(text=' * ', fg='black',
               command=lambda: press("*"), height=1, width=7)
bmult.grid(row=4, column=3)

bdiv = Button(text=' / ', fg='black',
              command=lambda: press("/"), height=1, width=7)
bdiv.grid(row=5, column=3)


bigual = Button(text=' = ', fg='black', command=equalpress, height=1, width=7)
bigual.grid(row=5, column=2)

bclear = Button(text='Clear', fg='black', command=clear, height=1, width=7)
bclear.grid(row=5, column='1')

ventana.mainloop()
