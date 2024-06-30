# Creditos a dabeaz,
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
# Diccionario para registrar los padres de cada nodo
padres = {}


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
def add_node(p_grafo, p_nodo):
    try:
        # Asegurarse de que p_nodo sea una instancia de Node
        if not isinstance(p_nodo, Node):
            # Convertir valor directo en un nuevo nodo con lista vacía de hijos
            p_nodo = Node(p_nodo, [])

        node_label = p_nodo.valor_nodo
        # Identifica al nodo
        node_name = f"node_{id(p_nodo)}"
        p_grafo.add_node(pydot.Node(node_name, label=node_label))

        for hijo in p_nodo.hijos:
            if isinstance(hijo, Node):
                hijo_nombre = f"node_{id(hijo)}"

                if hijo_nombre in padres:
                    # Si el hijo ya tiene un padre, creamos una copia del nodo hijo
                    nuevo_hijo = Node(hijo.valor_nodo, hijo.hijos)
                    add_node(p_grafo, nuevo_hijo)
                    nuevo_hijo_nombre = f"node_{id(nuevo_hijo)}"
                    p_grafo.add_edge(pydot.Edge(node_name, nuevo_hijo_nombre))
                else:
                    padres[hijo_nombre] = node_name
                    add_node(p_grafo, hijo)
                    p_grafo.add_edge(pydot.Edge(node_name, hijo_nombre))
            else:
                # Manejo de valores directos, convertimos a un nuevo nodo de tipo `Node`
                nuevo_hijo = Node(hijo, [])
                add_node(p_grafo, nuevo_hijo)
                nuevo_hijo_nombre = f"node_{id(nuevo_hijo)}"
                p_grafo.add_edge(pydot.Edge(node_name, nuevo_hijo_nombre))
    except Exception as e:
        print(f"Error en add_node: {e}")
        raise

# Clase para representar los nodos del árbol sintáctico


class Node:
    def __init__(self, valor_nodo, hijos=None):
        self.valor_nodo = valor_nodo
        self.hijos = hijos if hijos is not None else []

    def __repr__(self):
        return f"Node(valor_nodo={self.valor_nodo}, hijos={self.hijos})"

    def get_derivation(self, indent=0):
        """
        Obtiene la derivación del árbol sintáctico como una lista de reglas de producción.
        :param indent: Nivel de indentación para mostrar la estructura del árbol.
        :return: Lista de cadenas que representan la derivación.
        """
        derivation = []
        indent_str = '  ' * indent

        if self.hijos:
            regla = f"{self.valor_nodo} -> " + ' '.join(
                [str(hijo.valor_nodo) if isinstance(hijo, Node) else str(hijo) for hijo in self.hijos])
            derivation.append(indent_str + regla)

            for hijo in self.hijos:
                if isinstance(hijo, Node):
                    derivation.extend(hijo.get_derivation(indent + 1))
        else:
            derivation.append(indent_str + str(self.valor_nodo))

        return derivation


# Tokens para el analizador léxico
tokens = (
    'NUMERO',
    'SUMA',
    'MENOS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
)

# Definiciones de tokens
t_SUMA = r'\+'
t_MENOS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
# Definición de un número


def t_NUMERO(t):
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
def p_expression_SUMA(p):
    'expression : expression SUMA term'
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])

    print(f"Created Node: {p[0].valor_nodo} with hijos {p[0].hijos}")


def p_expression_MENOS(p):
    'expression : expression MENOS term'

    # Jere's idea
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])

    #   Mauri's idea
    #   p[0] = Node('OperacionBinaria', [p[1],'+',Node('Negativo',[p[2] ,p[3]])])


def p_factor_unary_minus(p):
    'factor : MENOS factor'
    p[0] = Node('Negativo', [p[1], p[2]])


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]
    print(f"Passing up term: {p[0]}")


def p_term_times(p):
    'term : term TIMES factor'
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])
    print(f"Created Node: {p[0].valor_nodo} with hijos {[p[1], p[3]]}")


def p_term_divide(p):
    'term : term DIVIDE factor'
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])
    print(f"Created Node: {p[0].valor_nodo} with hijos {[p[1],p[2], p[3]]}")


def p_term_factor(p):
    'term : factor'
    p[0] = p[1]
    print(f"Passing up factor: {p[0]}")


def p_factor_NUMERO(p):
    'factor : NUMERO'
    p[0] = Node('NUMERO', [p[1]])
    print(f"Created Node: NUMERO with value {p[1]}")


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = Node('PARENS', [Node('LPAREN', [p[1]]),
                p[2], Node('RPAREN', [p[3]])])


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


def evaluate(tree):
    if type(tree.hijos[0]) == int:
        return tree.hijos[0]
    elif tree.hijos[1] == '+':
        return evaluate(tree.hijos[0]) + evaluate(tree.hijos[2])
    elif tree.hijos[0] == '-':
        return -evaluate(tree.hijos[1])
    elif tree.hijos[1] == '*':
        return evaluate(tree.hijos[0]) * evaluate(tree.hijos[2])
    elif tree.hijos[1] == '/':
        return evaluate(tree.hijos[0]) / evaluate(tree.hijos[2])
    elif tree.hijos[0].hijos[0] == '(':
        return evaluate(tree.hijos[1])


def equalpress():
    global expression
    try:
        result = parser.parse(expression)

        analyze_expression()
        result_value = evaluate(result)

        equation.set(str(int(result_value)))
        expression = str(int(result_value))
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


def mostrarDerivacion():
    global expression
    try:
        result = parser.parse(expression)
        if isinstance(result, Node):
            derivation = result.get_derivation()
            derivation_str = '\n'.join(derivation)
            messagebox.showinfo(title="Derivación",
                                message="Derivación:\n" + derivation_str)
        else:
            messagebox.showerror(
                title="Error", message="No se pudo generar la derivación.")
    except Exception as e:
        messagebox.showerror(title="Error",
                             message="Se produjo un error: " + str(e))


def detail_tokens():
    global expression
    lexer.input(expression)
    tokens_detail = []
    derivations = ['Σ', 'S']
    tokens_detail.append(derivations)
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_detail.append(f'{tok.type}({tok.value})')
    messagebox.showinfo(title="Detalle de Tokens",
                        message=", ".join(tokens_detail))

 #


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
    ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('+', 2, 3),
    ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
    ('7', 4, 0), ('8', 4, 1), ('9', 4, 2), ('*', 4, 3),
    ('0', 5, 0), ('Clear', 5, 1), ('=', 5, 2), ('/', 5, 3),
    ('(', 6, 0), ('Analizar', 6, 1), ('Detalle', 6, 2),
    (')', 6, 3), ("Mostrar Árbol", 6, 2),

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
                        command=mostrarDerivacion, height=1, width=7)
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
