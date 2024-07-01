# Creditos a dabeaz por darnos una base
from tkinter import *
from tkinter import messagebox
import ply.lex as lex
import ply.yacc as yacc
import pydot

# Variables globales
derivations = ['Σ', 'S']
# para errores de sintaxis
syntax_error = False
# para la expresión
vExpression = ""
# Diccionario para registrar los padres de cada nodo
padres = {}


# Clase para representar los nodos del árbol sintáctico
class Node:
    def __init__(self, valor_nodo, hijos=None):
        self.valor_nodo = valor_nodo
        self.hijos = hijos if hijos is not None else []

    def __repr__(self):
        return f"Node(valor_nodo={self.valor_nodo}, hijos={self.hijos})"

    def get_forma_setencial(self, indent=0):
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
                    derivation.extend(hijo.get_forma_setencial(indent + 1))
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

# Modificación en las reglas de producción para crear nodos


def p_expression_SUMA(p):
    'expression : expression SUMA termino'
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])

    print(f"Created Node: {p[0].valor_nodo} with hijos {p[0].hijos}")


def p_expression_MENOS(p):
    'expression : expression MENOS termino'

    # Jere's idea
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])

    #   Mauri's idea
    #p[0] = Node('OperacionBinaria', [p[1], '+',Node('Negativo', [p[2], p[3]])])


def p_factor_unary_minus(p):
    'factor : MENOS factor'
    p[0] = Node('Negativo', [p[1], p[2]])


def p_expression_term(p):
    'expression : termino'
    p[0] = p[1]
    print(f"Passing up termino: {p[0]}")


def p_term_times(p):
    'termino : termino TIMES factor'
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])
    print(f"Created Node: {p[0].valor_nodo} with hijos {[p[1], p[3]]}")


def p_term_divide(p):
    'termino : termino DIVIDE factor'
    p[0] = Node('OperacionBinaria', [p[1], p[2], p[3]])
    print(f"Created Node: {p[0].valor_nodo} with hijos {[p[1],p[2], p[3]]}")


def p_term_factor(p):
    'termino : factor'
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


# Función para generar y graficar el árbol sintáctico
def generate_and_display_tree():
    global vExpression, syntax_error

    try:
        analyze_expression()
        syntax_error = False
        parser.parse(vExpression)
        if(not syntax_error):
            result = parser.parse(vExpression, tracking=True)
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
        clear()
        messagebox.showerror(
            title="Error", message="No se puede dividir por Cero")
    except Exception as e:
        equation.set("0")
        clear()
        messagebox.showerror(
            title="Error", message=f"Se produjo un error: {e}")


# Función recursiva para agregar nodos al árbol
def add_node(p_grafo, p_nodo, padres=None):
    if padres is None:
        padres = {}

    try:
        if not isinstance(p_nodo, Node):
            p_nodo = Node(p_nodo, [])

        node_label = p_nodo.valor_nodo
        node_name = f"node_{id(p_nodo)}"
        p_grafo.add_node(pydot.Node(node_name, label=node_label))

        for hijo in p_nodo.hijos:
            if isinstance(hijo, Node):
                hijo_nombre = f"node_{id(hijo)}"
                if hijo_nombre in padres:
                    nuevo_hijo = Node(hijo.valor_nodo, hijo.hijos)
                    add_node(p_grafo, nuevo_hijo, padres)
                    nuevo_hijo_nombre = f"node_{id(nuevo_hijo)}"
                    p_grafo.add_edge(pydot.Edge(node_name, nuevo_hijo_nombre))
                else:
                    padres[hijo_nombre] = node_name
                    add_node(p_grafo, hijo, padres)
                    p_grafo.add_edge(pydot.Edge(node_name, hijo_nombre))
            else:
                nuevo_hijo = Node(hijo, [])
                add_node(p_grafo, nuevo_hijo, padres)
                nuevo_hijo_nombre = f"node_{id(nuevo_hijo)}"
                p_grafo.add_edge(pydot.Edge(node_name, nuevo_hijo_nombre))
    except Exception as e:
        print(f"Error in add_node: {e}")
        raise

# Función para actualizar el contenido del visor


def press(num):
    global vExpression
    vExpression = vExpression + str(num)
    equation.set(vExpression)

# Función para evaluar la expresión final


def evaluate(tree):
    if type(tree.hijos[0]) == int:

        return tree.hijos[0]
    elif tree.hijos[1] == '+':
        return evaluate(tree.hijos[0]) + evaluate(tree.hijos[2])
    elif tree.hijos[1] == '-':
        return evaluate(tree.hijos[0])-evaluate(tree.hijos[2])
    elif tree.hijos[0] == '-':
        return -evaluate(tree.hijos[1])
    elif tree.hijos[1] == '*':
        return evaluate(tree.hijos[0]) * evaluate(tree.hijos[2])
    elif tree.hijos[1] == '/':
        return evaluate(tree.hijos[0]) / evaluate(tree.hijos[2])
    elif tree.hijos[0].hijos[0] == '(':
        return evaluate(tree.hijos[1])


def equalpress():
    global vExpression,syntax_error
    try:
        result = parser.parse(vExpression)
        analyze_expression()
        syntax_error = False
        if(not syntax_error):
        
            result_value = evaluate(result)
            equation.set(str(int(result_value)))
            vExpression = str(int(result_value))
    except ZeroDivisionError:
        clear()
        messagebox.showerror(
            title="Error", message="No se puede dividir por Cero")
    except Exception:
        clear()
        messagebox.showerror(title="Error", message="Se produjo un error")


# Función para analizar la expresión
def analyze_expression():
    global vExpression, syntax_error
    try:
        syntax_error = False
        parser.parse(vExpression)
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
    global vExpression
    try:
        result = parser.parse(vExpression)
        if isinstance(result, Node):
            derivation = result.get_forma_setencial()
            derivation_str = '\n'.join(derivation)
            messagebox.showinfo(title="Derivación",
                                message="Derivación:\n" + derivation_str)
        else:
            messagebox.showerror(
                title="Error", message="No se pudo generar la derivación.")
    except Exception as e:
        messagebox.showerror(title="Error",
                             message="Se produjo un error: " + str(e))


def mostrarDerivacionPorIzquierda():
    global vExpression
    try:
        result = parser.parse(vExpression)
        if isinstance(result, Node):
            derivationPorIzquierda = result.get_derivacion_por_izquierda()
            derivationPorIzquierda_str = '\n'.join(derivationPorIzquierda)
            messagebox.showinfo(title="Derivación",
                                message="Derivación:\n" + derivationPorIzquierda_str)
        else:
            messagebox.showerror(
                title="Error", message="No se pudo generar la derivación.")
    except Exception as e:
        messagebox.showerror(title="Error",
                             message="Se produjo un error: " + str(e))


def detail_tokens():
    global vExpression
    lexer.input(vExpression)
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

# Función para limpiar el contenido del visor


def clear():
    global vExpression
    vExpression = ""
    equation.set("")


def borrarUltimo():
    global vExpression
    # Verifica si la expresión no está vacía
    if vExpression:
        # Elimina el último carácter de la cadena
        vExpression = vExpression[:-1]
        # Actualiza el valor de la expresión en la interfaz
        equation.set(vExpression)
    else:
        # Si la expresión está vacía, asegúrate de que el valor mostrado también esté vacío
        clear()


# ***********Configuración de la interfaz gráfica********************
ventana = Tk()
ventana.title("Calculadora")
ventana.geometry("380x380")  # Ajuste del tamaño de la ventana

equation = StringVar()
visor = Entry(ventana, textvariable=equation, font=('Arial', 18),
              bd=10, insertwidth=2, width=25, borderwidth=4)
visor.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

clear()

# Creación de los botones
buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('=', 4, 1), ('<x|', 4, 2), ('+', 4, 3),
    ('Clear', 5, 0), ('(', 5, 1), (')', 5, 2), ('Analizar', 5, 3),
    ('Forma\nsentencial', 6, 0), ('Mostrar Árbol', 6, 1),
]

for (text, row, col) in buttons:
    if text == '=':
        button = Button(ventana, text=text, fg='black',
                        command=equalpress, height=2, width=10)
    elif text == 'Clear':
        button = Button(ventana, text=text, fg='black',
                        command=clear, height=2, width=10)
    elif text == 'Forma\nsentencial':
        button = Button(ventana, text=text, fg='black',
                        command=mostrarDerivacion, height=2, width=10)
    elif text == 'Analizar':
        button = Button(ventana, text=text, fg='black',
                        command=analyze_expression, height=2, width=10)
    elif text == "Mostrar Árbol":
        button = Button(ventana, text=text, fg='black',
                        command=generate_and_display_tree, height=2, width=10)
    elif text == "<x|":
        button = Button(ventana, text=text, fg='black',
                        command=borrarUltimo, height=2, width=10)
    else:
        button = Button(ventana, text=text, fg='black', bg='white',
                        command=lambda t=text: press(t), height=2, width=10)

    button.grid(row=row, column=col, padx=5, pady=5)

ventana.mainloop()
