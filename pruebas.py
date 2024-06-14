from tkinter import *
from tkinter import messagebox
import ply.lex as lex
import ply.yacc as yacc

# Tokens para el analizador léxico
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
)

# Definiciones de tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

# Definición de un número


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Ignorar espacios
t_ignore = ' \t'

# Manejo de errores léxicos


def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)


# Construcción del analizador léxico
lexer = lex.lex()

# Variable global para errores de sintaxis
syntax_error = False

# Definición de la gramática para el analizador sintáctico


def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = p[1] * p[3]


def p_term_divide(p):
    'term : term DIVIDE factor'
    p[0] = p[1] / p[3]


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]


def p_factor_number(p):
    'factor : NUMBER'
    p[0] = p[1]


def p_error(p):
    global syntax_error
    syntax_error = True
    print("Error de sintaxis")


# Construcción del analizador sintáctico
parser = yacc.yacc()

# Variable global para la expresión
expression = ""

# Función para actualizar el contenido del visor


def press(num):
    global expression
    expression = expression + str(num)
    equation.set(expression)

# Función para evaluar la expresión final


def equalpress():
    global expression
    try:
        result = parser.parse(expression)
        equation.set(str(result))
        expression = str(result)
    except ZeroDivisionError:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message="No se puede dividir por Cero")
    except Exception:
        equation.set("0")
        expression = ""
        messagebox.showerror(title="Error", message="Se produjo un error")

# Función para analizar la expresión


# Función para analizar la expresión
def analyze_expression():
    global expression, syntax_error
    try:
        syntax_error = False
        parser.parse(expression)
        if not syntax_error:
            messagebox.showinfo(
                title="Análisis", message="La expresión es válida")
        else:
            messagebox.showerror(title="Error de análisis",
                                 message="Error en la expresión")
    except Exception as e:
        messagebox.showerror(title="Error de análisis",
                             message="Error en la expresión: " + str(e))
        
# Función para detallar los tokens de la expresión
def detail_tokens():
    global expression
    lexer.input(expression)
    tokens_detail = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_detail.append(f'{tok.type}({tok.value})')
    messagebox.showinfo(title="Detalle de Tokens",
                        message=", ".join(tokens_detail))

# Función para limpiar el contenido del visor
def clear():
    global expression
    expression = ""
    equation.set("0")


# Configuración de la interfaz gráfica
ventana = Tk()
ventana.title("Calculadora")
ventana.geometry("365x175")  # Ajuste del tamaño de la ventana

equation = StringVar()
visor = Entry(textvariable=equation)
visor.config(state='disabled')
visor.grid(columnspan=4, ipadx=70)
equation.set('0')

# Creación de los botones
buttons = [
    ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('4', 3, 0),
    ('5', 3, 1), ('6', 3, 2), ('7', 4, 0), ('8', 4, 1),
    ('9', 4, 2), ('0', 5, 0), ('+', 2, 3), ('-', 3, 3),
    ('*', 4, 3), ('/', 5, 3), ('=', 5, 2), ('Clear', 5, 1),
    ('Analizar', 6, 1), ('Detalle', 6, 2)
]

for (text, row, col) in buttons:
    if text == '=':
        button = Button(text=text, fg='black',
                        command=equalpress, height=1, width=7)
    elif text == 'Clear':
        button = Button(text=text, fg='black',
                        command=clear, height=1, width=7)
    elif text == 'Analizar':
        button = Button(text=text, fg='black',
                        command=analyze_expression, height=1, width=7)
    elif text == 'Detalle':
        button = Button(text=text, fg='black',
                        command=detail_tokens, height=1, width=7)
    else:
        button = Button(text=text, fg='black', bg='white',
                        command=lambda t=text: press(t), height=1, width=7)
    button.grid(row=row, column=col)

ventana.mainloop()
