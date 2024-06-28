from tkinter import *
from tkinter import messagebox
import ply.lex as lex
import ply.yacc as yacc
import pydot

# pydot.graphviz.set_graphviz_executables(
#   dot=r'C:\Program Files\Graphviz\bin\dot.exe')

# Variables globales
derivations = ['Σ', 'S']
# para errores de sintaxis
syntax_error = False
# para la expresión
expression = ""


# Función para generar y graficar el árbol sintáctico
# Función para generar y graficar el árbol sintáctico
def generate_and_display_tree():
    global expression

    try:
        result = parser.parse(expression, tracking=True)
        print(f"Parser result: {result}")
        if isinstance(result, Node):
            graph = pydot.Dot(graph_type='graph')
            add_node(graph, result)
            graph.write_png('syntax_tree.png')
            messagebox.showinfo(title="Árbol Sintáctico",
                                message="Árbol generado correctamente. Ver 'syntax_tree.png'.")
        else:
            messagebox.showerror(
                title="Error", message="No se pudo generar el árbol sintáctico.")
    except ZeroDivisionError:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message="No se puede dividir por Cero")
    except Exception as e:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message=f"Se produjo un error: {e}")

# Función recursiva para agregar nodos al árbol


def add_node(graph, node):
    try:
        if isinstance(node, Node):
            node_label = node.op
        else:
            node_label = str(node)

        node_name = f"node_{id(node)}"
        graph.add_node(pydot.Node(node_name, label=node_label))

        if isinstance(node, Node):
            for child in node.children:
                child_name = f"node_{id(child)}"
                add_node(graph, child)
                graph.add_edge(pydot.Edge(node_name, child_name))
    except Exception as e:
        print(f"Error en add_node: {e}")
        raise

# Clase para representar los nodos del árbol sintáctico


class Node:
    def __init__(self, op, children=None):
        self.op = op
        self.children = children if children else []

    def __repr__(self):
        return f"Node({self.op}, {self.children})"


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


# Definición de la gramática para el analizador sintáctico


# Modificación en las reglas de producción para crear nodos
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = Node('+', [p[1], p[3]])
    print(f"Created Node: {p[0].op} with children {[p[1], p[3]]}")


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = Node('-', [p[1], p[3]])
    print(f"Created Node: {p[0].op} with children {[p[1], p[3]]}")


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]
    print(f"Passing up term: {p[0]}")


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = Node('*', [p[1], p[3]])
    print(f"Created Node: {p[0].op} with children {[p[1], p[3]]}")


def p_term_divide(p):
    'term : term DIVIDE factor'
    p[0] = Node('/', [p[1], p[3]])
    print(f"Created Node: {p[0].op} with children {[p[1], p[3]]}")


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]
    print(f"Passing up factor: {p[0]}")


def p_factor_number(p):
    'factor : NUMBER'
    p[0] = Node('NUMBER', [p[1]])
    print(f"Created Node: NUMBER with value {p[1]}")


def p_error(p):
    global syntax_error
    syntax_error = True
    print("Error de sintaxis")


# Construcción del analizador sintáctico
parser = yacc.yacc()


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
    global expression, syntax_error
    global derivations
    try:
        syntax_error = False
        parser.parse(expression)
        if not syntax_error:
            derivation_str = "\n".join(derivations)
            messagebox.showinfo(title="Derivación", message=derivation_str)
        else:
            messagebox.showerror(title="Error de análisis",
                                 message="Error en la expresión")
    except Exception as e:
        messagebox.showerror(title="Error de análisis",
                             message="Error en la expresión: " + str(e))
    derivations = ['Σ', 'S']


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
    ('Analizar', 6, 1), ('Detalle', 6, 2), ("Mostrar Árbol", 6, 2)
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
    elif text == "Mostrar Árbol":
        button_show_tree = Button(text="Mostrar Árbol", fg='black',
                                  command=generate_and_display_tree, height=1, width=15)
        button_show_tree.grid(row=6, column=4)

    else:
        button = Button(text=text, fg='black', bg='white',
                        command=lambda t=text: press(t), height=1, width=7)
    button.grid(row=row, column=col)

ventana.mainloop()
