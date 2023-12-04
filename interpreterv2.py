from brewparse import parse_program
from intbase import InterpreterBase
from intbase import ErrorType
from copy import deepcopy, copy
from env_v1 import EnvironmentManager


#environment stack
#create a dictionary of variables for each function


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False): super().__init__(console_output, inp) 
    
    def run(self, program):
        ast = parse_program(program)
        print(ast)
        self.__set_up_function_table(ast)
        self.variable_name_to_value = dict()
        main_func_node = self.get_main_func_node(ast)
        self.env = EnvironmentManager()
        self.run_main_func(main_func_node)
    
    def __set_up_function_table(self, ast):
        self.func_name_to_ast = {}
        for func_def in ast.get("functions"):
            self.func_name_to_ast[func_def.get("name")] = func_def

    def get_main_func_node(self, ast):
        check_main = 0
        main_node = None
        x = self.func_list[0]
        for x in self.func_list:
            if x.get("name") == "main":
                check_main = check_main + 1
                main_node = x
        if check_main <= 1:
            return main_node
        else:
            return super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",)
    
    def run_main_func(self, main_func_node):
       self.var_dict = dict()
       for statement in main_func_node.get("statements"):      
           self.run_statement(statement)
    
    def run_func(self, func_node, param_dict):
        statements = func_node.get("statements")
        if len(param_dict) != []:
            for x in statements:
                self.run_func_statement(x, param_dict)
        else:
            for x in statements:
                self.run_statement(x)

    def run_func_statement(self, statement_node, param_dict):
        if self.is_assignment(statement_node):
            self.do_func_assignment(statement_node, param_dict)
        elif self.is_func_call(statement_node):
            self.do_func_call(statement_node)
        elif self.is_if_statement(statement_node):
            self.do_if_statement(statement_node)
        elif self.is_while_loop(statement_node):
            self.do_while_loop(statement_node)

    def run_statement(self, statement_node):
        if self.is_assignment(statement_node):
            self.do_assignment(statement_node)
        elif self.is_func_call(statement_node):
            self.do_func_call(statement_node)
        elif self.is_if_statement(statement_node):
            self.do_if_statement(statement_node)
        elif self.is_while_loop(statement_node):
            self.do_while_loop(statement_node)
    
    def is_assignment(self, statement_node):
        if statement_node.elem_type == "=":
            return 1
        else:
            return 0
        
    def is_func_call(self, statement_node):
        if statement_node.elem_type == "fcall":
            return 1
        else:
            return 0
    
    def is_if_statement(self, statement_node):
        if statement_node.elem_type == "if":
            return 1
        else:
            return 0
    
    def do_if_statement(self, statement_node):
        condition = statement_node.get("condition")
        statements = statement_node.get("statements")
        else_statements = statement_node.get("else_statements")
        if self.evaluate_condition(condition) == "true":
            for x in statements:
                self.run_statement(x)
        else:
            if else_statements != None:
                for x in else_statements:
                    self.run_statement(x)

    def evaluate_condition(self, condition):
        if self.is_variable_node(condition):
            if self.get_value_of_variable(condition) == "true" or self.get_value_of_variable(condition) == "false":
                return self.get_value_of_variable(condition)
            else:
                super().error(
                ErrorType.NAME_ERROR,
                f"Does not evaluate to Boolean",)
        elif self.is_binary_comparison(condition):
            return self.evaluate_binary_comparison(condition)
        elif self.is_boolean_node(condition):
            return self.get_bool(condition)
        elif self.is_logical_comparison(condition):
            return self.evaluate_logical_comparison(condition)
        elif self.is_logical_unary(condition):
            return self.evaluate_logical_unary(condition)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Does not evaluate to Boolean",)
            
    def is_while_loop(self, statement_node):
        if statement_node.elem_type == "while":
            return 1
        else:
            return 0

    def do_while_loop(self, statement_node):
        condition = statement_node.get("condition")
        statements = statement_node.get("statements")
        while self.evaluate_condition(condition) == "true":
            for x in statements:
                self.run_statement(x)

    def do_assignment(self, statement_node):
        target_var_name = self.get_target_variable_name(statement_node)
        source_node = self.get_expression_node(statement_node)
        resulting_value = self.evaluate_expression(source_node)
        self.variable_name_to_value[target_var_name] = resulting_value

    def do_func_assignment(self, statement_node, param_dict):
        target_var_name = self.get_target_variable_name(statement_node)
        source_node = self.get_expression_node(statement_node)
        resulting_value = self.evaluate_expression(source_node)
        param_dict[target_var_name] = resulting_value

    def get_target_variable_name(self, statement_node):
        return statement_node.get("name")

    def get_expression_node(self, statement_node):
        return statement_node.get("expression")

    def evaluate_expression(self, expression_node):
        if self.is_value_node(expression_node):
            return self.get_value(expression_node)
        elif self.is_variable_node(expression_node):
            return self.get_value_of_variable(expression_node)
        elif self.is_binary_operator(expression_node):
            return self.evaluate_binary_operator(expression_node)
        elif self.is_unary_operator(expression_node):
            return self.evaluate_unary_operator(expression_node)
        elif self.is_binary_comparison(expression_node):
            return self.evaluate_binary_comparison(expression_node)
        elif self.is_boolean_node(expression_node):
            return self.get_bool(expression_node)
        elif self.is_logical_comparison(expression_node):
            return self.evaluate_logical_comparison(expression_node)
        elif self.is_logical_unary(expression_node):
            return self.evaluate_logical_unary(expression_node)
        elif self.is_func_call(expression_node):
            if self.is_input_i(expression_node):
                return self.do_input_i(expression_node)
            else:
                super().error(
                ErrorType.NAME_ERROR,
                f"Bad function bro",)

    def is_value_node(self, expression_node):
        if (expression_node.elem_type == "int"):
            return 1
        elif (expression_node.elem_type == "string"):
            return 1
        else:
            return 0
        
    def get_value(self, expression_node):
        return expression_node.dict["val"]
    
    def is_variable_node(self, expression_node):
        if expression_node.elem_type == "var":
            return 1
        else:
            return 0
        
    def get_value_of_variable(self, expression_node):
        name_of_var = expression_node.get("name")
        if name_of_var not in self.variable_name_to_value:
            super().error(
            ErrorType.NAME_ERROR,
            f"Variable {name_of_var} has not been defined",)
        else:
            return self.variable_name_to_value[expression_node.get("name")]
        
    def is_boolean_node(self, expression_node):
        if expression_node.elem_type == "bool":
            return 1
        else:
            return 0

    def get_bool(self, expression_node):
        return expression_node.dict["val"]
    
    def print_bool(self, expression_node):
        boolean = self.get_bool(expression_node)
        if boolean == True:
            return "true"
        else:
            return "false"
    
    def is_binary_operator(self, expression_node):
        if expression_node.elem_type == "+":
            return 1
        elif expression_node.elem_type == "-":
            return 1
        elif expression_node.elem_type == "*":
            return 1
        elif expression_node.elem_type == "/":
            return 1
        else:
            return 0
        
    def is_unary_operator(self, expression_node):
        if expression_node.elem_type == "neg":
            return 1
        else:
            return 0
        
    def is_binary_comparison(self, expression_node):
        if expression_node.elem_type == "==":
            return 1
        elif expression_node.elem_type == "!=":
            return 1
        elif expression_node.elem_type == "<":
            return 1
        elif expression_node.elem_type == "<=":
            return 1
        elif expression_node.elem_type == ">":
            return 1
        elif expression_node.elem_type == "=>":
            return 1
        else:
            return 0
    
    def is_logical_unary(self, expression_node):
        if expression_node.elem_type == "!":
            return 1
        else:
            return 0

    def is_logical_comparison(self, expression_node):
        if expression_node.elem_type == "||":
            return 1
        elif expression_node.elem_type == "&&":
            return 1
        else:
            return 0
    
    def evaluate_logical_comparison(self, expression_node):
        op1 = expression_node.get("op1")
        op2 = expression_node.get("op2")
        operand1 = self.get_op_1(op1)
        operand2 = self.get_op_2(op2)
        if (operand1 == "true" or operand1 == "false") and (operand2 == "true" or operand2 == "false"):
            if expression_node.elem_type == "||":
                if operand1 == "true" or operand2 == "true":
                    return "true"
                else:
                    return "false"
            elif expression_node.elem_type == "&&":
                if operand1 == "true" and operand2 == "true":
                    return "true"
                else:
                    return "false"
        else:
            super().error(
              ErrorType.TYPE_ERROR,
              "Incompatible types for logical comparison",)
    
    def evaluate_logical_unary(self, expression_node):
        op1 = expression_node.get("op1")
        operand1 = self.get_op_1(op1)
        if (operand1 == "true" or operand1 == "false"):
            if operand1 == "true":
                return "false"
            elif operand1 == "false":
                return "true"
        else:
            super().error(
              ErrorType.TYPE_ERROR,
              "Incompatible type for logical comparison",)

    def evaluate_binary_operator(self, expression_node):
        op1 = expression_node.get("op1")
        op2 = expression_node.get("op2")
        operand1 = self.get_op_1(op1)
        operand2 = self.get_op_2(op2)
        if type(operand1) != type(operand2):
             super().error(
              ErrorType.TYPE_ERROR,
              "Incompatible types for arithmetic operation",)
        else:
            if type(operand1) == str and type(operand2) == str:
                if expression_node.elem_type == "+":
                    return (operand1 + operand2)
                else:
                    super().error(
                    ErrorType.TYPE_ERROR,
                    "Cannot perform this operation on strings",)
            else:
                if expression_node.elem_type == "+":
                    return (operand1 + operand2)
                elif expression_node.elem_type == "-":
                    return (operand1 - operand2)
                elif expression_node.elem_type == "*":
                    return (operand1 * operand2)
                elif expression_node.elem_type == "/":
                    return (operand1 // operand2)
    
    def evaluate_unary_operator(self, expression_node):
        op1 = expression_node.get("op1")
        operand1 = self.get_op_1(op1)
        if type(operand1) != int:
            super().error(
              ErrorType.TYPE_ERROR,
              "Incompatible type for arithmetic operation",)
        else:
            return (- operand1)

    def evaluate_binary_comparison(self, expression_node):
        op1 = expression_node.get("op1")
        op2 = expression_node.get("op2")
        operand1 = self.get_op_1(op1)
        operand2 = self.get_op_2(op2)
        if expression_node.elem_type == "==" or expression_node.elem_type == "!=":
            if expression_node.elem_type == "==":
                if type(operand1) != type(operand2):
                    return "false"
                elif ((operand1 == "true" or operand1 == "false") and (operand2 == "true" or operand2 == "false")) or (type(operand1) == str and type(operand2) == str) or (type(operand1) == int and type(operand2) == int):
                    if operand1 == operand2:
                        return "true"
                    else:
                        return "false"
                else: 
                    super().error(
                    ErrorType.TYPE_ERROR,
                    "Incompatible types for binary operation",)
            elif expression_node.elem_type == "!=":
                if operand1 != operand2:
                    return "true" 
                else:
                    return "false" 
        else:
            if type(operand1) != type(operand2):
                super().error(
                ErrorType.TYPE_ERROR,
                "Incompatible types for binary operation",)
            else:
                if expression_node.elem_type == "<":
                    if operand1 < operand2:
                        return "true"
                    else:
                        return "false"
                elif expression_node.elem_type == "<=":
                    if operand1 <= operand2:
                        return "true"
                    else:
                        return "false"
                elif expression_node.elem_type == ">=":
                    if operand1 >= operand2:
                        return "true"
                    else:
                        return "false"
                elif expression_node.elem_type == ">":
                    if operand1 > operand2:
                        return "true"
                    else:
                        return "false"

    def do_func_call(self, statement_node):
        function_name = statement_node.get("name")
        if function_name == "print":
            resulting_value = ""
            for x in statement_node.get("args"):
                if self.is_value_node(x):
                    resulting_value = resulting_value + str(self.get_value(x))
                elif self.is_variable_node(x):
                    resulting_value = resulting_value + str(self.get_value_of_variable(x))
                elif self.is_binary_operator(x):
                    resulting_value = resulting_value + str(self.evaluate_expression(x))
                elif self.is_input_i(x):
                    self.do_input_i(x)
                elif self.is_unary_operator(x):
                    resulting_value = resulting_value + str(self.evaluate_unary_operator(x))
                elif self.is_binary_comparison(x):
                    resulting_value = resulting_value + str(self.evaluate_binary_comparison(x))
                elif self.is_boolean_node(x):
                    resulting_value = resulting_value + str(self.print_bool(x))
                elif self.is_logical_comparison(x):
                    resulting_value = resulting_value + str(self.evaluate_logical_comparison(x))
                elif self.is_logical_unary(x):
                    resulting_value = resulting_value + str(self.evaluate_logical_unary(x))
            super().output(resulting_value)
        elif function_name == "inputi":
            self.do_input_i(statement_node)
        elif self.is_defined_function(statement_node):
            args = statement_node.get("args")
            self.do_defined_function(statement_node, args)
        else:
            super().error(
            ErrorType.NAME_ERROR,
            f"Bad function bro",)

    def is_defined_function(self, statement_node):
        name = statement_node.get("name")
        if name not in self.func_name_to_ast:
            super().error(ErrorType.NAME_ERROR, f"Function {name} not found")
        else:
            return 1

    def do_defined_function(self, statement_node, args):
        evaluated_params = []
        evaluated_params = list(map(self.evaluate_expression, args))
        for x in self.func_list:
            if x.get("name") == statement_node.get("name") and len(x.get("args")) == len(statement_node.get("args")):
                self.param_name_to_value = dict() 
                z = 0; 
                for y in x.get("args"):
                    self.param_name_to_value[self.evaluate_argument_node(y)] = evaluated_params[z]
                    z = z + 1
                print(self.param_name_to_value)
                self.run_func(x, self.param_name_to_value)

    def evaluate_argument_node(self, argument_node):
        parameter = argument_node.get("name")
        return parameter

    def is_input_i(self, se_node):
        function_name = se_node.get("name")
        if function_name == "inputi":
            return 1
        else:
            return 0
    
    def do_input_i(self, se_node):
        if se_node.get("args") == []:
            user_input = super().get_input()
            return int(user_input)
        elif len(se_node.get("args")) == 1:
            arg = se_node.get("args")[0]
            prompt = arg.get("val")
            super().output(prompt)
            user_input = super().get_input()
            return int(user_input)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"No inputi() function found that takes > 1 parameter",)
            
    def get_op_1(self, op1):
        if self.is_value_node(op1):
            return self.get_value(op1)
        elif self.is_variable_node(op1):
            return self.get_value_of_variable(op1)
        elif self.is_binary_operator(op1):
            return self.evaluate_expression(op1)
        elif self.is_input_i(op1):
            return self.do_input_i(op1)
        elif self.is_unary_operator(op1):
            return self.evaluate_unary_operator(op1)
        elif self.is_binary_comparison(op1):
            return self.evaluate_binary_comparison(op1)
        elif self.is_boolean_node(op1):
            return self.print_bool(op1)
        elif self.is_logical_comparison(op1):
            return self.evaluate_logical_comparison(op1)
        elif self.is_logical_unary(op1):
            return self.evaluate_logical_unary(op1)

    def get_op_2(self, op2):
        if self.is_value_node(op2):
            return self.get_value(op2)
        elif self.is_variable_node(op2):
             return self.get_value_of_variable(op2)
        elif self.is_binary_operator(op2):
             return self.evaluate_expression(op2)
        elif self.is_input_i(op2):
            return self.do_input_i(op2)
        elif self.is_unary_operator(op2):
            return self.evaluate_unary_operator(op2)
        elif self.is_binary_comparison(op2):
            return self.evaluate_binary_comparison(op2)
        elif self.is_boolean_node(op2):
            return self.print_bool(op2)
        elif self.is_logical_comparison(op2):
            return self.evaluate_logical_comparison(op2)
        elif self.is_logical_unary(op2):
            return self.evaluate_logical_unary(op2)
         






#--------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------

def main():
# all programs will be provided to your i
# interpreter as a list of # python strings, just as shown here.
    program_source = """
                        func second(x, y) {
                            print(x);
                            }

                        func main() {
                            p = "disha";
                            q = 10 + 11;
                            second(p, q);
                            
                            }
                    """
  # this is how you use our parser to parse a valid Brewin program into
  # an AST:
    interpreter = Interpreter()
    interpreter.run(program_source)



if __name__ == "__main__":
    main()








            
        
