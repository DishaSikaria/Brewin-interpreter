from brewparse import parse_program
from intbase import InterpreterBase
from intbase import ErrorType

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False): super().__init__(console_output, inp) 
    
    def run(self, program):
        ast = parse_program(program)   
        self.variable_name_to_value = dict()  
        main_func_node = self.get_main_func_node(ast)
        self.run_func(main_func_node)

    def get_main_func_node(self, ast):
        main_node = ast.get("functions")[0]
        if (main_node.get("name")) == "main":
            return ast.get("functions")[0] 
        else:
            return super().error(
                ErrorType.NAME_ERROR,
                "No main() function was found",)
    
    def run_func(self, main_func_node):
       for statement in main_func_node.get("statements"):      
           self.run_statement(statement)
            
    def run_statement(self, statement_node):
        if self.is_assignment(statement_node):
            self.do_assignment(statement_node)
        elif self.is_func_call(statement_node):
            self.do_func_call(statement_node)
    
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
        
    def do_assignment(self, statement_node):
        target_var_name = self.get_target_variable_name(statement_node)
        source_node = self.get_expression_node(statement_node)
        resulting_value = self.evaluate_expression(source_node)
        self.variable_name_to_value[target_var_name] = resulting_value

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
    
    def is_binary_operator(self, expression_node):
        if expression_node.elem_type == "+":
            return 1
        elif expression_node.elem_type == "-":
            return 1
        else:
            return 0

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
            if expression_node.elem_type == "+":
                return (operand1 + operand2)
            elif expression_node.elem_type == "-":
                return (operand1 - operand2)

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
            super().output(resulting_value)
        elif function_name == "inputi":
            self.do_input_i(statement_node)
        else:
            super().error(
                ErrorType.NAME_ERROR,
                f"Bad function bro",)

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
    
    def get_op_2(self, op2):
        if self.is_value_node(op2):
            return self.get_value(op2)
        elif self.is_variable_node(op2):
             return self.get_value_of_variable(op2)
        elif self.is_binary_operator(op2):
             return self.evaluate_expression(op2)
        elif self.is_input_i(op2):
            return self.do_input_i(op2)
         







            
        
