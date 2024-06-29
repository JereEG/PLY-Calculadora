from tkinter import *
from tkinter import messagebox
import ply.lex as lex
import ply.yacc as yacc
import pydot
# import os

# Configura la ruta del ejecutable 'dot'
# os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'

# Clase para representar los nodos del árbol sintáctico


class Node:
    def __init__(self, op, children=None):
        self.op = op
        self.children = children if children else []

    def __str__(self):
        return f"{self.op}({', '.join(str(child) for child in self.children)})"


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


def t_NUMBER(t):
    r'\d+'
    t.value = Node('NUMBER', [t.value])
    return t


t_ignore = ' \t'


def t_error(t):
    print(f"Caracter ilegal '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()

# Reglas de precedencia
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = Node('+', [p[1], p[3]])


def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = Node('-', [p[1], p[3]])


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = Node('*', [p[1], p[3]])


def p_term_divide(p):
    'term : term DIVIDE factor'
    p[0] = Node('/', [p[1], p[3]])


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


parser = yacc.yacc()

# Variables globales
derivations = ['Σ', 'S']
syntax_error = False
expression = ""

# Función recursiva para agregar nodos al árbol


def add_node(graph, node):
    if isinstance(node, Node):
        node_name = f"node_{id(node)}"
        node_label = node.op if node.op != 'NUMBER' else str(node.children[0])
        graph.add_node(pydot.Node(node_name, label=node_label))

        for child in node.children:
            child_name = f"node_{id(child)}"
            add_node(graph, child)
            graph.add_edge(pydot.Edge(node_name, child_name))
    else:
        # Handle the case where node is an integer (leaf node for number)
        node_name = f"node_{id(node)}"
        node_label = str(node)
        graph.add_node(pydot.Node(node_name, label=node_label))


# Función para generar y graficar el árbol sintáctico


def generate_and_display_tree():
    global expression, derivations

    try:
        derivations = []
        result = parser.parse(expression, tracking=True)
        equation.set(str(result))
        expression = str(result)

        graph = pydot.Dot(graph_type='graph')
        add_node(graph, result)
        graph.write_png('syntax_tree.png')

        messagebox.showinfo(title="Árbol Sintáctico",
                            message="Árbol generado correctamente. Ver 'syntax_tree.png'.")
    except ZeroDivisionError:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message="No se puede dividir por Cero")
    except Exception as e:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message=f"Se produjo un error: {str(e)}")


def press(num):
    global expression
    expression = expression + str(num)
    equation.set(expression)


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
    except Exception as e:
        equation.set("0")
        expression = ""
        messagebox.showerror(
            title="Error", message=f"Se produjo un error: {str(e)}")


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


def clear():
    global expression
    expression = ""
    equation.set("0")


ventana = Tk()
ventana.title("Calculadora")
ventana.geometry("365x175")

equation = StringVar()
visor = Entry(textvariable=equation)
visor.config(state='disabled')
visor.grid(columnspan=4, ipadx=70)
equation.set('0')

buttons = [
    ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('4', 3, 0),
    ('5', 3, 1), ('6', 3, 2), ('7', 4, 0), ('8', 4, 1),
    ('9', 4, 2), ('0', 5, 0), ('+', 2, 3), ('-', 3, 3),
    ('*', 4, 3), ('/', 5, 3), ('=', 5, 2), ('Clear', 5, 1),
    ('Analizar', 6, 1), ('Detalle', 6, 2), ("Mostrar Árbol", 6, 3)
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
        button = Button(text=text, fg='black',
                        command=generate_and_display_tree, height=1, width=12)
    else:
        button = Button(text=text, fg='black',
                        command=lambda t=text: press(t), height=1, width=7)
    button.grid(row=row, column=col)

ventana.mainloop()
