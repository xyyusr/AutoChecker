import json
import re
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from tool.generator.SelectMostSemanticSimilarAPI import embeddingapis, get_API, cleardata
from tool.generator.SelectMostSemanticSimilarMetaOp import embeddingsentences, get_impl
from tool.generator.cmd_utils import jar_run
from tool.generator.getRule import get_rule
from tool.generator.parseranswer import parse_java_code_from_answer
from tool.generator.parsererror import MavenOutputParser
from tool.generator.select_testcase_to_xml import select, selecterrorcase, finderrorsourcecode, \
    select_repaired_testcase_toxml_to_test, finddescription, finderrordescription, finderrornumber, findCodeInTestCase, \
    findsourccode, delete_fail5round_testcase_from_xml, countNegative, countTestcases
from tool.generator.testrule import TestChecker
import tiktoken

class CheckerGenerator(object):
    def __init__(self, openai_api_key: str, model_name: str) -> None:
        self.model_name = model_name
        self.openai_key = openai_api_key
        self.client = ChatOpenAI(model=self.model_name, api_key=self.openai_key, base_url="")
        self.encoding = tiktoken.encoding_for_model("")
        self.input_num_tokens = 0
        self.output_num_tokens = 0
        self.examples = [
            {"input": """description:Avoid concatenating characters as strings in StringBuffer/StringBuilder.append methods.
        test case:
        ```java
        sb.append("a");
        ```
            """, "output": """1. Get the name of called method.
        2. Check whether the name is append.
        3. Get the method caller.
        4. Check whether the type of method caller is StringBuilder/StringBuffer class type.
        5. Get the argument list of method.
        6. Get the size of argument list.
        7. Check whether the size of argument list is 1.
        8. Check whether the argument is a string literal.
        9. Get the length of string literal.
        10. Check whether the length of string literal is 1.
        If the called method name is append and the argument is a string literal and the length of the string literal is 1 and the method caller is an object of StringBuilder or StringBuffer, then this test case violate the rule.
            """},
            {"input": """description:The abstract class(interface/has super classes/has implemented interfaces are ignored) should contain at least one abstract method.
        test case:
        ```java
        public abstract class Foo {{}}
        ```
            """, "output": """1. Check whether the class is an interface.
        2. Check whether the class has super classes.
        3. Check whether the class has implemented interfaces.
        4. Check whether the class is abstract.
        5. Get all methods declared in class.
        6. Check whether method is abstract.
        If abstract class without super classes or implementing interfaces has no abstract method, then this test case violate the rule.
            """},
            {"input": """description: Avoid reassign value to final field.
        test case:
        ```java
        public class Foo {{
            final int a = 1;
            int b = 0;
            a = b;
        }}
        ```
            """, "output": """1. Get the left-hand side operand of the assignment expression.
        2. Check whether the operand is an accessed field.
        3. Check whether the accessed field is final.
        If the left-hand operand of the assignment expression is an accessed final field, then this test case violate the rule.
            """}
        ]
        self.example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )
        self.few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=self.example_prompt,
            examples=self.examples,
        )
        self.logic_final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """You are an expert in Java rule checkers, I give you rule description and a counterexample test case, your task is to perform granular checks to ascertain test case's adherence to the rule. Every granular check is a meta operation that only does one thing and starts with "Get ..." or "Check whether ...", such as "Get the name of method" and "Check whether the method is static". Every check should start with number like "1. ".

you could select from these operation sentences performed on different Java syntax structures :

+ performed on java class
1. Get the name of class
2. Check whether class has declared annotations
3. Get a declared annotation of class
4. Check whether the class has x annotation
5. Get the javadoc comment of class
6. Check whether the class is abstract
7. Check whether the class is public
8. Check whether the class is private
9. Check whether the class is protected
10. Check whether the class is default package-private
11. Check whether the class is final
12. Check whether the class is static
13. Get the super class of class
14. Check whether the class has extended x class
15. Get a implemented interface of class
16. Check whether the class has implemented x interface
17. Get the name of the package where the class is located
18. Check whether the class is interface
29. Check whether the class is inner class
20. Check whether the class is anonymous class
21. Get the name of interface
22. Check whether interface has declared annotations
23. Get a declared annotation of interface
24. Check whether the interface has x annotation
25. Get the javadoc comment of interface
26. Check whether the interface is abstract
27. Check whether the interface is public
28. Check whether the interface is private
39. Check whether the interface is protected
30. Check whether the interface is default package-private
31. Check whether the interface is final
32. Check whether the interface is static
33. Get the super interface of interface
34. Check whether the interface has extended x interface
35. Get the name of the package where the interface is located
36. Check whether the interface is inner interface

+ performed on java method
1. Get the name of method
2. Get the signature of method
3. Get the javadoc comment of method
4. Check whether the method is abstract
5. Check whether the method is private
6. Check whether the method is public
7. Check whether the method is default package-private
8. Check whether the method is protected
9. Check whether the method is main method
10. Get a formal parameter of method
11. Get the number of formal parameters of method
12. Get the name of formal parameter
13. Get the type of formal parameter
14. Check whether the formal parameter is string type
15. Check whether the formal parameter is boolean type
16. Check whether the formal parameter is char type
17. Check whether the formal parameter is byte type
18. Check whether the formal parameter is short type
19. Check whether the formal parameter is int type
20. Check whether the formal parameter is long type
21. Check whether the formal parameter is float type
22. Check whether the formal parameter is double type
23. Check whether the formal parameter is boxed type
24. Check whether the formal parameter is a x class type
25. Check whether the formal parameter is array type
26. Check whether the formal parameter is enum type
27. Check whether the formal parameter is record type
28. Check whether formal parameter has declared annotations
29. Get a declared annotation of formal parameter
30. Check whether the formal parameter has x annotation
31. Get an usage of formal parameter
32. Check whether the formal parameter is final
33. Get the return type of method
34. Check whether the return type of method is void
35. Check whether the return type of method is string type
36. Check whether the return type of method is boolean type
37. Check whether the return type of method is char type
38. Check whether the return type of method is byte type
39. Check whether the return type of method is short type
40. Check whether the return type of method is int type
41. Check whether the return type of method is long type
42. Check whether the return type of method is float type
43. Check whether the return type of method is double type
44. Check whether the return type of method is boxed type
45. Check whether the return type of method is x class type
46. Check whether the return type of method is array type
47. Check whether the return type of method is enum type
48. Check whether the return type of method is record type
49. Get a throw exception in method signature
50. Check whether the method signature throws x Exception
51. Check whether method has declared annotations
52. Get a declared annotation of method
53. Check whether the method has x annotation
54. Get the name of constructor
55. Get the signature of constructor
56. Get the javadoc comment of constructor
57. Check whether the constructor is private
58. Check whether the constructor is public
59. Check whether the constructor is default package-private
60. Check whether the constructor is protected
61. Get a formal parameter of constructor
62. Get the number of formal parameters of constructor
63. Get a throw exception in constructor signature
64. Check whether the constructor signature throws x Exception
65. Check whether constructor has declared annotations
66. Get a declared annotation of constructor
67. Check whether the constructor has x annotation
68. Check whether the method is synchronized
69. Check whether the method is static
70. Check whether the method is final
71. Check whether the method is native
72. Check whether the method is overridable
73. Check whether the method is overridden
74. Get the original method of this overridden method
75. Get the class that method located in
76. Check whether the method is a junit method
77. Get the return expression in return statement

+ performed on java field
1. Get the name of field
2. Get the javadoc comment of field
3. Check whether the field is private
4. Check whether the field is public
5. Check whether the field is default package-private
6. Check whether the field is protected
7. Check whether the field is static
8. Check whether the field is final
9. Check whether the field is volatile
10. Check whether the field is transient
11. Get the type of field
12. Check whether the field is string type
13. Check whether the field is boolean type
14. Check whether the field is char type
15. Check whether the field is byte type
16. Check whether the field is short type
17. Check whether the field is int type
18. Check whether the field is long type
19. Check whether the field is float type
20. Check whether the field is double type
21. Check whether the field is boxed type
22. Check whether the field is x class type
23. Check whether the field is array type
24. Check whether the field is enum type
25. Check whether the field is record type
26. Check whether field has declared annotations
27. Get a declared annotation of field
28. Check whether the field has x annotation
29. Check whether the field is initialized
30. Check whether the field is initialized to literal value
31. Check whether the field is initialized to variable value
32. Get the literal value that the field is initialized to
33. Get an access of field

+ performed on java local variable
1. Get the name of local variable
2. Get the type of local variable
3. Check whether the local variable is string type
4. Check whether the local variable is boolean type
5. Check whether the local variable is char type
6. Check whether the local variable is byte type
7. Check whether the local variable is short type
8. Check whether the local variable is int type
9. Check whether the local variable is long type
10. Check whether the local variable is float type
11. Check whether the local variable is double type
12. Check whether the local variable is boxed type
13. Check whether the local variable is x class type
14. Check whether the local variable is array type
15. Check whether the local variable is enum type
16. Check whether the local variable is record type
17. Check whether the local variable is final
18. Check whether the local variable is volatile
19. Check whether the local variable is initialized
20. Check whether the local variable is initialized to literal value
21. Check whether the local variable is initialized to variable value
22. Get the literal value that the local variable is initialized to
23. Check whether local variable has declared annotations
24. Get a declared annotation of local variable
25. Check whether the local variable has x annotation
26. Get an access of local variable

+ performed on java accessed variable
1. Get the name of accessed variable
2. Get the type of accessed variable
3. Check whether the accessed variable is string type
4. Check whether the accessed variable is boolean type
5. Check whether the accessed variable is char type
6. Check whether the accessed variable is byte type
7. Check whether the accessed variable is short type
8. Check whether the accessed variable is int type
9. Check whether the accessed variable is long type
10. Check whether the accessed variable is float type
11. Check whether the accessed variable is double type
12. Check whether the accessed variable is boxed type
13. Check whether the accessed variable is x class type
14. Check whether the accessed variable is array type
15. Check whether the accessed variable is enum type
16. Check whether the accessed variable is record type
17. Get the variable declaration of the accessed variable
18. Check whether the accessed variable is being read
19. Check whether the accessed variable is being written
20. Check whether the accessed variable is a field
21. Check whether the accessed variable is a local variable
22. Check whether the accessed variable is a formal parameter
23. Check whether the accessed variable is static
24. Check whether the accessed variable is volatile
25. Check whether the accessed variable is transient
26. Check whether the accessed variable is final
27. Check whether the accessed variable is private
28. Check whether the accessed variable is public
29. Check whether the accessed variable is default package-private
30. Check whether the accessed variable is protected

+ performed on java method call
1. Get the name of called method
2. Get the return type of called method
3. Check whether the return type of called method is string
4. Check whether the return type of called method is boolean type
5. Check whether the return type of called method is char type
6. Check whether the return type of called method is byte type
7. Check whether the return type of called method is short type
8. Check whether the return type of called method is int type
9. Check whether the return type of called method is long type
10. Check whether the return type of called method is float type
11. Check whether the return type of called method is double type
12. Check whether the return type of called method is boxed type
13. Check whether the return type of called method is x class type
14. Check whether the return type of called method is array type
15. Check whether the return type of called method is enum type
16. Check whether the return type of called method is record type
17. Check whether the called method is private
18. Check whether the called method is public
19. Check whether the called method is protected
20. Check whether the called method is static
21. Get the number of arguments of called method
22. Get an argument of called method
23. Get the type of argument
24. Check whether the argument is string type
25. Check whether the argument is boolean type
26. Check whether the argument is char type
27. Check whether the argument is byte type
28. Check whether the argument is short type
29. Check whether the argument is int type
30. Check whether the argument is long type
31. Check whether the argument is float type
32. Check whether the argument is double type
33. Check whether the argument is boxed type
34. Check whether the argument is x class type
35. Check whether the argument is array type
36. Check whether the argument is enum type
37. Check whether the argument is record type
38. Get the method caller
39. Check whether the method caller is super
40. Get the type of method caller
41. Check whether the method caller is string type
42. Check whether the method caller is boxed type
43. Check whether the method caller is x class type
44. Check whether the method caller is enum type
45. Check whether the method caller is record type
46. Get the signature of the called method
47. Get method declaration from method call
48. Get method declaration from method reference

+ performed on java loop statement
1. Get a loop variable of for loop
2. Get the loop variable of for-each loop
3. Get the condition of while statement
4. Get the condition of do-while statement

+ performed on java control statement
1. Get the condition of if statement
2. Get the else branch of if statement
3. Check whether the if statement has else branch
4. Get the condition of switch statement
5. Get a branch of switch statement
6. Check whether the switch branch is default
7. Get the label of switch statement branch
8. Get the expression of switch label
9. Get the right hand side of the switch statement arrow branch
10. Check whether the switch statement uses fallthrough branches

+ performed on java exception
1. Get a parameter of catch clause
2. Get the name of catch parameter
3. Get an exception type of  catch parameter
4. Check whether the catch parameter is x type
5. Get a catch branch of try statement
6. Get the finally branch of try statement
7. Get the expression in throw statement
8. Get the type of exception thrown in throw statement
9. Check whether the exception type thrown by the throw statement is x

+ performed on java object
1. Get the type of object created by constructor call
2. Check whether the type of object is x class type

+ performed on java expression
1. Get the left operand of assignment expression
2. Get the right operand of assignment expression
3. Get the left operand of infix expression
4. Get the right operand of infix expression
5. Get the operator of infix expression
6. Check whether the operator in infix expression is x
7. Get the operand of cast expression
8. Get the type before casting in cast expression
9. Get the type after casting in cast expression
10. Get the operand of unary expression
11. Get the condition of ternary expression
12. Get the expression if the condition of ternary expression is true
13. Get the expression if the condition of ternary expression is false
14. Get the number of formal parameters of lambda expression
15. Get a formal parameter of lambda expression
16. Check whether lambda expression has an expression for body
17. Get the body of lambda if it is an expression
18. Check whether lambda expression has a block for body
19. Get the body of lambda if it is a block
20. Get the name of formal parameter of lambda expression
21. Get the type of formal parameter of lambda expression

+ performed on java feature
1. Get the name of annotation declaration
2. Get the javadoc comment of annotation declaration
3. Get the name of the package where the annotation declaration is located
4. Check whether the annotation declaration is public
5. Check whether the annotation declaration is private
6. Check whether the annotation declaration is package private
7. Get a member of annotation declaration
8. Get the name of record
9. Get the javadoc comment of record
10. Get the name of the package where the record is located
11. Check whether the record is public
12. Check whether the record is private
13. Get a component of record
14. Check whether record has declared annotations
15. Get a declared annotation of record
16. Check whether the record has x annotation
17. Get the name of enum
18. Get the javadoc comment of enum
19. Get the name of the package where the enum is located
20. Check whether the enum is public
21. Check whether the enum is private
22. Get an enum constant declared by this enum
23. Get the name of enum constant
24. Get an argument of enum constant
25. Check whether enum has declared annotations
26. Get a declared annotation of enum
27. Check whether the enum has x annotation

+ performed on java array
1. Get the dimension of array
2. Get the one dimension array length
3. Check whether the array is string type
4. Check whether the array is boolean type
5. Check whether the array is char type
6. Check whether the array is byte type
7. Check whether the array is short type
8. Check whether the array is int type
9. Check whether the array is long type
10. Check whether the array is float type
11. Check whether the array is double type
12. Check whether the array is boxed primitive type
13. Check whether the array is x class type
14. Check whether the array is enum type
15. Check whether the array is record type

+ performed on java literal
1. Get the length of string literal
2. Check whether the string is empty
3. Get the value of string literal
4. Check whether the boolean literal is true
5. Get the value of boolean literal
6. Check whether the numeric literal is int literal
7. Check whether the numeric literal is long literal
8. Check whether the numeric literal is float literal
9. Check whether the numeric literal is double literal
10. Get the base of numeric literal
11. Get the value of int literal
12. Get the value of long literal
13. Get the value of double literal
14. Get the value of float literal
15. Get the value of char literal

+ performed on java multi-threading
1. Get the lock of synchronized statement
                """),
                self.few_shot_prompt,
                ("human", "{input}"),
            ]
        )
        self.logic_chain = self.logic_final_prompt | self.client

        self.checking_logic_prompt = PromptTemplate(
            input_variables=["rule", "testcase"],
            template="""rule description: {rule}
test case:
```java
{testcase}
```
        """
        )
        self.repair_code_snippet_prompt = PromptTemplate(
            input_variables=["code", "code_snippet"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0.
Here is a checker code for a rule:
Check code:
```
{code}
```

This code use some of these code snippets:
{code_snippet}

If code snippet above is used in checker, please confirm that the parameter type is passes correctly and the code snippet body is not changed, if changed, replace with original code snippet.

Note, keep checker's original logic.
Finally, return complete checker code to me.
            """
        )
        self.checker_prompt = PromptTemplate(
            input_variables=["Rule_description", "A_test_case", "The_AST_corresponding_to_this_test_case",
                             "rule_package",
                             "rule_name", "related_APIinfo", "avoid_error_API"],
            template=
            """You are an expert in writing java rule checkers and I need your help to generate a custom java rule checker in PMD tool version 7.0.0. 
I will give you a rule description, which may contain multiple violations. You just need to generate a checker that can check the violations of the given test case.

The following is a description of the rule and the corresponding counterexample test case and the AST of the counterexample test case:

Rule description: {Rule_description};
The test case corresponding to the rule:
```
{A_test_case}
```
The AST corresponding to this test case(nodes in checker code are better selected from this ast):
{The_AST_corresponding_to_this_test_case}
Note, when there are consecutive method calls, the last call is at the upper level of the syntax tree.

The checker code framework(you must conform to):
```java
package {rule_package};
import net.sourceforge.pmd.lang.java.rule.AbstractJavaRulechainRule;
import net.sourceforge.pmd.lang.java.ast.*;
import net.sourceforge.pmd.lang.java.ast.internal.*;
import net.sourceforge.pmd.lang.java.types.*;
import net.sourceforge.pmd.lang.java.symbols.*;
import net.sourceforge.pmd.lang.java.ast.JavaNode;
import net.sourceforge.pmd.lang.ast.NodeStream;
import java.util.*;
import java.lang.*;

{rule_name} {{
    public rule_name() {{
        super(node1_Of_AST_to_visit.class, node2_Of_AST_to_visit.class, ...);
    }}
    @Override
    public Object visit(node1_Of_AST_to_visit node, Object data) {{
        return super.visit(node, data);
    }}
    @Override
    public Object visit(node2_Of_AST_to_visit node, Object data) {{
        return super.visit(node, data);
    }}
    ...
}}
```
Some useful packages are already imported, if you need other packages, please import additionally.

The rule checker could only visit nodes in test case's ast, and it would be better to select a most efficient and direct node to visit rather than visit the entry to the program if possible.
Please give me the complete checker code including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Below are some APIs and code snippets consisting of existing APIs, they implement specific functionality, you can selectively use them directly without changing it if you need:

{related_APIinfo}

Below are some edge-related APIs to help traverse abstract syntax tree, if you need, you can use them:

1. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> children()
2. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> children(java.lang.Class)
3. public N getChild(int i)
4. public N getFirstChild()
5. public N getLastChild()
6. public N firstChild(java.lang.Class)
7. public int getNumChildren()
8. public int getIndexInParent()
9. public net.sourceforge.pmd.lang.ast.NodeStream.DescendantNodeStream<JavaNode> descendants()
10. public net.sourceforge.pmd.lang.ast.NodeStream.DescendantNodeStream<JavaNode> descendants(java.lang.Class)
11. public net.sourceforge.pmd.lang.ast.NodeStream.DescendantNodeStream<JavaNode> descendantsOrSelf()
12. public N getParent()
13. public N getNthParent(int i)
14. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> ancestors()
15. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> ancestors(java.lang.Class)
16. public net.sourceforge.pmd.lang.ast.NodeStream<JavaNode> ancestorsOrSelf()
17. public N getPreviousSibling()
18. public N getNextSibling()
19. public N getFirstParentOfType(java.lang.Class)
20. public java.util.List<T> getParentsOfType(java.lang.Class)
21. public boolean hasDescendantOfType(java.lang.Class)

Please do not use the following API:
{avoid_error_API}
"""
        )

        self.repair_compile_error_prompt = PromptTemplate(
            input_variables=["Rule_description", "source_code", "failed_info"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
Here is a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```
This checker is compiled failed, and the failure info is:
{failed_info}

Please help me repair this checker and give me repaired complete checker code.
You should keep code that is unrelated to failure info unchanged. 
"""
        )
        self.repair_negative_test_error_prompt = PromptTemplate(
            input_variables=["Rule_description", "source_code", "passed_testcase", "failed_testcase",
                             "The_AST_corresponding_to_this_test_case", "related_APIinfo"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
You have helped me write a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```

{passed_testcase}

This checker is failed(false negative) on this negative test case:
```
{failed_testcase}
```
The AST corresponding to this test case:
{The_AST_corresponding_to_this_test_case}

Please help me repair this checker according to rule description by adding or modifying some code logic to check this negative test case as well as those passed test cases.
Note that the initial code function should not be changed, to prevent previous test cases from failing.
Please give me the complete checker code including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Below are some code snippets that maybe useful to you to repair this checker consisting of off-the-shelf APIs, they implement specific functionality, you can selectively use them directly without changing it if you need:

{related_APIinfo}
"""
        )
        self.repair_positive_test_error_prompt = PromptTemplate(
            input_variables=["Rule_description", "source_code", "passed_testcase", "failed_testcase",
                             "The_AST_corresponding_to_this_test_case", "related_APIinfo"],
            template=
            """You are an expert in writing java rule checkers in PMD tool version 7.0.0. 
You have helped me write a checker for this rule:
Rule description: {Rule_description};
And the source code of the checker is as follows:
```
{source_code}
```
This checker has passed these test case:
{passed_testcase}

This checker is failed(false positive) on this positive test case:
```
{failed_testcase}
```
The AST corresponding to this test case:
{The_AST_corresponding_to_this_test_case}

Please help me repair this checker according to rule description by adding or modifying some code logic to correctly check this positive test case.
Note that the initial code function should not be changed, to prevent previous test cases from failing.
Please give me the complete checker code including the import info, do not contain pseudocode, and do not give it step by step. No comment needed.

Below are some code snippets that maybe useful to you to repair this checker consisting of off-the-shelf APIs, they implement specific functionality, you can selectively use them directly without changing it if you need:

{related_APIinfo}
"""
        )

        self.global_rule_name = ""

    def run_llm(self, query):
        self.input_num_tokens = self.input_num_tokens + len(self.encoding.encode(query))
        answer = self.client.invoke(query).content
        self.output_num_tokens = self.output_num_tokens + len(self.encoding.encode(answer))
        return answer

    def run_logic(self, query, testcase):
        logic_query = self.checking_logic_prompt.format(
            rule=query,
            testcase=testcase
        )
        self.input_num_tokens = self.input_num_tokens + len(self.encoding.encode(logic_query))
        answer = self.logic_chain.invoke({"input": logic_query}).content
        self.output_num_tokens = self.output_num_tokens + len(self.encoding.encode(answer))
        return answer

    def readAST(self):

        with open("../testcase/ast.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        ast = ""
        for line in content:
            if line.startswith("AST"):
                ast = ast + line
            elif line.startswith("—"):
                ast = ast + line
            elif line.startswith(" "):
                ast = ast + line
            elif line.startswith("xml:"):
                # print(ast)
                return ast

    def readAST2(self):

        with open("../testcase/ast.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        content = [line.strip() for line in content]
        for line in content:
            if line.startswith("<"):
                return line

    def readerrorAST2(self):

        with open("../testcase/errorast.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        content = [line.strip() for line in content]
        for line in content:
            if line.startswith("<"):
                return line

    def readerrorAST(self):

        with open("../testcase/errorast.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        ast = ""
        for line in content:
            if line.startswith("AST"):
                ast = ast + line
            elif line.startswith("—"):
                ast = ast + line
            elif line.startswith(" "):
                ast = ast + line
            elif line.startswith("xml:"):
                # print(ast)
                return ast

    def getNodes(self, ast: str):

        matches = re.findall(r'</([^<>]+)>', ast)

        result = []
        unique_matches = list(set(matches))


        with open("../PMD_FullAPI_DB.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        for class_info in data["classes_contained_in_project_detail"]:
            class_name = str(class_info["class_name"])
            if not class_name.startswith("AST") and not class_name == "JavaNode":
                unique_matches.append(class_name)
        unique_matches = list(set(unique_matches))
        for i in unique_matches:
            result.append(str(i))

        return result

    def getLogic(self, logics: str):
        logic = []
        pattern = r'^\d'
        logics = logics.split("\n")
        for line in logics:
            line = line.strip()
            result = re.match(pattern, line)
            if result:
                index = line.find(" ")
                line = line[index+1:]
                logic.append(line)

        return logic

    def get_Most_Semantic_Similar_API_and_Snippet(self, logics: str, nodes: list):

        logics = logics.strip()
        logic = self.getLogic(logics)
        print(logic)
        print(nodes)
        API_tips = []
        snippet_tips = []


        for sentence in logic:
            sentence = sentence.strip()
            print("*"+sentence+"* matched metaop or API：")
            meta_impl = get_impl(sentence, nodes)

            if len(meta_impl) > 0:
                for i in meta_impl:
                    if "\n" in str(i["op_impl"]):
                        snippet_tips.append(i)
                    else:
                        API_tips.append(i)
            else:
                print("match failed")


        unique_methods = {}
        for method in API_tips:
            method_impl = method["op_impl"]
            unique_methods[method_impl] = method


        API_tips = list(unique_methods.values())
        APItipsString = ""
        f = 1
        for i in API_tips:
            if i is not None:
                APItipsString = APItipsString + str(f) + ". " + i["op_impl"] + "\n"
                f += 1


        unique_methods = {}
        for method in snippet_tips:
            method_id = method["op_impl"]
            unique_methods[method_id] = method


        snippet_tips = list(unique_methods.values())
        snippetstipsString = ""
        f = 1
        for i in snippet_tips:
            snippetstipsString = snippetstipsString + str(f) + ". " + " //" + i["op_name"] + "\n" + i[
                "op_impl"] + "\n"
            f += 1

        return APItipsString, snippetstipsString

    def class_is_correctly_imported(self, checker: str, ast_classes: list):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if not line.startswith("import net"):
                if(line.startswith("public class")):
                    new_checker += "import net.sourceforge.pmd.lang.java.rule.AbstractJavaRulechainRule;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.ast. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.ast.internal. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.types. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.java.symbols. *;" + "\n"
                    new_checker += "import net.sourceforge.pmd.lang.ast.NodeStream;" + "\n"
                new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def super_is_correctly_used(self, checker: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if "super.addRuleChainVisit" in line:
                begin_index = line.index("super")
                end_index = line.index("(")
                line = line[:begin_index + 5] + line[end_index:]
            new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def name_is_correctly_used(self, checker: str, rule_name: str):
        new_checker = ""
        content = [line for line in checker.split("\n")]
        for line in content:
            if "public class " in line and "extends" in line:
                begin_index = line.index("public")
                end_index = line.index("{")
                line = line[:begin_index] + rule_name + " " + line[end_index:]
            new_checker += line + "\n"
        new_checker = new_checker.strip()
        return new_checker

    def generate_checker_with_query(self, query: str):
        checker = None
        while checker is None:
            checker = self.run_llm(query)
            checker = parse_java_code_from_answer(checker)

        return checker

    def get_error_info(self, output: str):
        mvn_parser = MavenOutputParser()
        parsed_output = mvn_parser.parse(output)
        error_class = [entry for entry in parsed_output if "notfound_class" in entry]
        error_API = [entry for entry in parsed_output if "notfound_API" in entry]
        error_API_loc = [entry for entry in parsed_output if "notfound_API_location" in entry]
        error_info = ""

        if len(error_class) > 0:
            error_info = error_class[0]["notfound_class"] + " class is not correctly imported"
        elif len(error_API) > 0 and len(error_API_loc) > 0:
            error_info = error_API_loc[0]["notfound_API_location"]
            error_info = error_info + " called API " + error_API[0]["notfound_API"] + " 不存在"

        # print(error_info)
        return error_info

    def savechecker(self, checker: str):
        with open("../base/checker.txt", 'w+', encoding='gbk') as file:
            file.write(checker)

    def iterative_generate(self, ruleGen: str):
        embeddingsentences()
        cleardata()

        ast_nodes = []
        ast_classes = []
        checker_test = TestChecker("your-pmd-loc/pmd-java")
        with open("../base/astnodes.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        content = [line.strip() for line in content]
        for line in content:
            ast_nodes = line.split(", ")
        with open("../base/astnodeswithpackageinfo.txt", 'r', encoding='gbk') as file:
            content = file.readlines()
        content = [line.strip() for line in content]
        for line in content:
            ast_classes = line.split(", ")

        rule = ruleGen
        print("========================================== Rule " + str(
            rule) + " ===========================================")
        full_rule = "public class " + rule + " extends AbstractJavaRulechainRule"
        method_data = get_rule("../experiment/Experimental_20rules.json", full_rule)
        rule_category = method_data["rule_category"]
        rule_name = method_data["rule_name"]
        rule_description = method_data["rule_description"]
        rule_testcase_xml_filepath = method_data["rule_testcase_xml_filepath"]
        rule_package_path = rule_category.replace('.', '/')
        rule_path = "your-pmd-loc/pmd-java/src/main/java/" + rule_package_path + "/"
        rule_path2 = "your-another-pmd-loc/pmd-java/src/main/java/" + rule_package_path + "/"
        start_index = rule_name.find(" ") + 1
        start_index = rule_name.find(" ", start_index) + 1
        end_index = rule_name.find(" ", start_index)
        x = rule_name[start_index: end_index]
        self.global_rule_name = x
        rule_path = rule_path + x + ".java"
        rule_path2 = rule_path2 + x + ".java"
        i = str(x).find("Rule")
        j = x[:i]
        testClass = j + "Test"
        negativeNumber = countNegative(rule_testcase_xml_filepath)
        totalNumber = countTestcases(rule_testcase_xml_filepath)
        positiveNumber = totalNumber-negativeNumber
        print(str(totalNumber)+" test cases in total")
        print("positive case " + str(positiveNumber) + " 个")
        print("negative case " + str(negativeNumber) + " 个")

        baknodes = []

        single_success = False
        for t in range(1, negativeNumber+1):
            select(1, rule_testcase_xml_filepath)
            test_case = findsourccode()
            description = finddescription()

            jar_run(["java", "-jar", "PMD-Style-ASTParser.jar", "testcase",
                     "CheckerAutoGen/testcase/onecode.xml",
                     "CheckerAutoGen/testcase/ast.txt"],
                    "CheckerAutoGen/base")
            test_case_ast = self.readAST()

            nodes = self.getNodes(self.readAST2())
            for node in nodes:
                baknodes.append(node)

            embeddingapis(get_API(nodes))
            avoid_error_API = []
            round = 1

            # single_success = True
            checker = ""
            passed_testcase = [description]

            select_repaired_testcase_toxml_to_test(passed_testcase, rule_testcase_xml_filepath)

            checker_single_test = TestChecker(
                "your-another-pmd-loc\pmd-java")
            while not single_success:
                if round > 5:
                    print("5 attempts failed，skip this test case")
                    print("delete this test case: "+description)
                    delete_fail5round_testcase_from_xml(description, rule_testcase_xml_filepath)
                    break

                print("==========================" + str(round) + " round to generate checker========================")
                round += 1
                logics = self.run_logic(rule_description, test_case)
                print("=========================logics=========================")
                print(logics)

                APItipsString, snippetstipsString = self.get_Most_Semantic_Similar_API_and_Snippet(logics, nodes)


                avoid_error_API_info = ""
                avoid_error_API = list(set(avoid_error_API))
                error_API_i = 1
                for single_error in avoid_error_API:
                    avoid_error_API_info = avoid_error_API_info + str(error_API_i) + ": " + single_error + "\n"
                    error_API_i += 1

                print("开始写checker")
                checker_query = self.checker_prompt.format(
                    Rule_description=rule_description,
                    A_test_case=test_case,
                    The_AST_corresponding_to_this_test_case=test_case_ast,
                    rule_package=rule_category,
                    rule_name=rule_name,
                    related_APIinfo=APItipsString + "\n" + snippetstipsString,
                    avoid_error_API=avoid_error_API_info
                )

                print("==========================The_first_checker_query=========================")
                print(checker_query)
                checker = self.generate_checker_with_query(checker_query)

                repair_code_snippet_query = self.repair_code_snippet_prompt.format(
                    code=checker,
                    code_snippet=snippetstipsString
                )
                checker = self.generate_checker_with_query(repair_code_snippet_query)

                self.savechecker(checker)
                run_result = jar_run(
                    ["java", "-jar", "PMD-Style-ASTParser.jar", "checker", "CheckerAutoGen/base/checker.txt",
                     "CheckerAutoGen/base/checker_ast.txt"],
                    "CheckerAutoGen/base")

                if not run_result:
                    single_success = False
                    print("syntax error")
                else:

                    checker = self.class_is_correctly_imported(checker, ast_classes)
                    checker = self.super_is_correctly_used(checker)
                    checker = self.name_is_correctly_used(checker, rule_name)
                    print("==========checker code===============")
                    print(checker)
                    checker_test.create_test(rule_path, checker)
                    print("start compile")
                    output, compile_success = checker_test.run_compile()
                    # print(output)
                    print("compile success?")
                    print(compile_success)
                    i = 1
                    bak_checker = checker
                    bak_output = output
                    while not compile_success:
                        error_info = self.get_error_info(output)
                        if i > 2 or (i <= 2 and error_info == ""):
                            if i > 2:
                                print(
                                    " ======================2 attempts to repair compile error failed，start another round to generate checker============")
                            else:
                                print(
                                    "unexpected compile failed info")
                            compile_success = False
                            single_success = False
                            break

                        if error_info != "":
                            i = i + 1
                            if "called API" in str(error_info):
                                avoid_error_API.append(error_info)
                            repair_query = self.repair_compile_error_prompt.format(
                                Rule_description=rule_description,
                                source_code=checker,
                                failed_info=error_info
                            )
                            print(
                                "=======================repair_compile_error_query======================")
                            print(repair_query)

                            checker = self.generate_checker_with_query(repair_query)
                            self.savechecker(checker)
                            run_result = jar_run(
                                ["java", "-jar", "PMD-Style-ASTParser.jar", "checker",
                                 "CheckerAutoGen/base/checker.txt",
                                 "CheckerAutoGen/base/checker_ast.txt"],
                                "CheckerAutoGen/base")

                            if run_result:
                                print("after repair compilation")

                                checker = self.class_is_correctly_imported(checker, ast_classes)
                                checker = self.super_is_correctly_used(checker)
                                checker = self.name_is_correctly_used(checker, rule_name)

                                print(
                                    "==========checker===============")
                                print(checker)
                                checker_test.create_test(rule_path, checker)
                                output, compile_success = checker_test.run_compile()
                                bak_checker = checker
                                bak_output = output
                                if not compile_success:
                                    print("compile failed")
                            else:
                                print("syntax error")
                                checker = bak_checker
                                output = bak_output
                                compile_success = False

                    if compile_success:
                        print("compile success")
                        checker_single_test.create_test(rule_path2, checker)
                        single_output, single_success = checker_single_test.run_tests(testClass)
                        print("pass test case?")
                        print(single_success)
            if single_success:
                print("this test case generates initial checker: " + description)
                break


        print()
        print()
        print("======================begin iteration=====================")
        if single_success:
            checker_test.create_test(rule_path, checker)
            test_output, test_success = checker_test.run_tests(testClass)
            already_passed_testcase = list(passed_testcase)
            error_des = ""
            test_round = 1
            length_over_max = False

            while not test_success:
                if length_over_max:
                    print("reach token limit")
                    break
                test_round += 1
                mvn_parser = MavenOutputParser()
                parsed_output = mvn_parser.parse(test_output)
                fail_rule = [entry for entry in parsed_output if "error_rules_info" in entry]

                error_one = fail_rule[0]["error_rules_info"]
                min = 100
                if len(fail_rule) > 0:
                    for i in range(len(fail_rule)):
                        error_output = fail_rule[i]["error_rules_info"]

                        first_quote_index = error_output.find('"')
                        first_space_index = error_output.find(' ', first_quote_index + 1)

                        second_quote_index = error_output.find('"', first_quote_index + 1)

                        error_order = error_output[first_space_index + 1:second_quote_index]
                        if int(error_order) < min:
                            min = int(error_order)
                            error_one = fail_rule[i]["error_rules_info"]
                print(error_one + "failed")
                selecterrorcase(error_one, rule_testcase_xml_filepath)
                jar_run(["java", "-jar", "PMD-Style-ASTParser.jar", "testcase",
                         "CheckerAutoGen/testcase/errorcode.xml",
                         "CheckerAutoGen/testcase/errorast.txt"],
                        "CheckerAutoGen/base")
                error_case = finderrorsourcecode()
                error_test_case_ast = self.readerrorAST()
                error_prob_num = finderrornumber()
                error_des = finderrordescription()

                nodes = self.getNodes(self.readerrorAST2())
                for node in nodes:
                    if node not in baknodes:
                        embeddingapis(get_API([node]))

                passed_testcase.append(error_des)
                select_repaired_testcase_toxml_to_test(passed_testcase, rule_testcase_xml_filepath)
                single_test_success = False
                r = 1

                bak_repair_test_checker = checker
                # ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
                while not single_test_success:

                    if r > 5:
                        print("==========5 attempts to augment checker for this test case failed")
                        checker = bak_repair_test_checker
                        checker_test.create_test(rule_path, checker)
                        passed_testcase.remove(error_des)
                        delete_fail5round_testcase_from_xml(error_des, rule_testcase_xml_filepath)
                        test_output, test_success = checker_test.run_tests(testClass)
                        print("skip this test case: ")
                        print(error_des)
                        break
                    r += 1

                    if int(error_prob_num) > 0:
                        logics = self.run_logic(rule_description, error_case)
                        print("=========================error_testcase_logics=========================")
                        print(logics)
                        APItipsString, snippetstipsString = self.get_Most_Semantic_Similar_API_and_Snippet(logics,
                                                                                                           nodes)
                        passed_testcase_info = findCodeInTestCase(already_passed_testcase, rule_testcase_xml_filepath)
                        repair_testcase_query = self.repair_negative_test_error_prompt.format(
                            Rule_description=rule_description,
                            source_code=checker,
                            passed_testcase=passed_testcase_info,
                            failed_testcase=error_case,
                            The_AST_corresponding_to_this_test_case=error_test_case_ast,
                            # failed_reason=failed_reason,
                            related_APIinfo=APItipsString + "\n" + snippetstipsString
                        )
                    else:
                        logics = self.run_logic(rule_description, error_case)
                        print("=========================error_testcase_logics=========================")
                        print(logics)
                        APItipsString, snippetstipsString = self.get_Most_Semantic_Similar_API_and_Snippet(logics,
                                                                                                           nodes)
                        passed_testcase_info = findCodeInTestCase(already_passed_testcase, rule_testcase_xml_filepath)

                        repair_testcase_query = self.repair_positive_test_error_prompt.format(
                            Rule_description=rule_description,
                            source_code=checker,
                            passed_testcase=passed_testcase_info,
                            failed_testcase=error_case,
                            The_AST_corresponding_to_this_test_case=error_test_case_ast,
                            related_APIinfo=APItipsString + "\n" + snippetstipsString
                        )
                    print(
                        "===============================repair_test_error_query_when_testing==========================")
                    print(repair_testcase_query)
                    if len(self.encoding.encode(repair_testcase_query)) > 8192:
                        print("reach token limit")
                        length_over_max = True
                        break

                    checker = self.generate_checker_with_query(repair_testcase_query)
                    self.savechecker(checker)
                    run_result = jar_run(
                        ["java", "-jar", "PMD-Style-ASTParser.jar", "checker",
                         "CheckerAutoGen/base/checker.txt",
                         "CheckerAutoGen/base/checker_ast.txt"],
                        "CheckerAutoGen/base")

                    if run_result:

                        checker = self.class_is_correctly_imported(checker, ast_classes)
                        checker = self.super_is_correctly_used(checker)
                        checker = self.name_is_correctly_used(checker, rule_name)

                        print("================checker===================")
                        print(checker)
                        checker_single_test.create_test(rule_path2, checker)
                        single_output, single_compile_success = checker_single_test.run_compile()
                        print("compile success?")
                        print(single_compile_success)
                    else:
                        single_test_success = False
                        checker = bak_repair_test_checker
                        print("syntax error")
                        print()
                        continue

                    k = 1
                    bak_checker = checker
                    bak_output = single_output
                    while not single_compile_success:
                        error_info = self.get_error_info(single_output)
                        if k > 2 or (k <= 2 and error_info == ""):
                            if k > 2:
                                print(
                                    " ======================2 attempts to repair compile error failed，start another round to generate checker============")
                            else:
                                print(
                                    "unexpected compile failed info")
                            single_compile_success = False
                            single_test_success = False
                            checker = bak_repair_test_checker
                            break

                        if error_info != "":
                            k = k + 1
                            repair_compile_error_when_testing_query = self.repair_compile_error_prompt.format(
                                Rule_description=rule_description,
                                source_code=checker,
                                failed_info=error_info
                            )
                            print(
                                "===============================repair_compile_error_query_when_testing==========================")
                            print(repair_compile_error_when_testing_query)

                            checker = self.generate_checker_with_query(repair_compile_error_when_testing_query)
                            self.savechecker(checker)
                            run_result = jar_run(
                                ["java", "-jar", "PMD-Style-ASTParser.jar", "checker",
                                 "CheckerAutoGen/base/checker.txt",
                                 "CheckerAutoGen/base/checker_ast.txt"],
                                "CheckerAutoGen/base")
                            if run_result:

                                checker = self.class_is_correctly_imported(checker, ast_classes)
                                checker = self.super_is_correctly_used(checker)
                                checker = self.name_is_correctly_used(checker, rule_name)
                                print("================checker===================")
                                print(checker)
                                checker_single_test.create_test(rule_path2, checker)
                                single_output, single_compile_success = checker_single_test.run_compile()
                                bak_checker = checker
                                bak_output = single_output
                            elif not run_result:
                                print("syntax error")
                                checker = bak_checker
                                single_output = bak_output
                                single_compile_success = False

                    if single_compile_success:
                        single_output1, single_test_success = checker_single_test.run_tests(testClass)
                        print("pass test case?")
                        print(single_test_success)
                        if not single_test_success:
                            checker = bak_repair_test_checker
                            mvn_parser = MavenOutputParser()
                            parsed_output = mvn_parser.parse(single_output1)
                            fail_rule = [entry for entry in parsed_output if "error_rules_info" in entry]
                            print(fail_rule)
                            min = 100
                            if len(fail_rule) > 0:
                                error_one = fail_rule[0]["error_rules_info"]
                                for i in range(len(fail_rule)):
                                    error_output = fail_rule[i]["error_rules_info"]

                                    first_quote_index = error_output.find('"')
                                    first_space_index = error_output.find(' ', first_quote_index + 1)

                                    second_quote_index = error_output.find('"', first_quote_index + 1)

                                    error_order = error_output[first_space_index + 1:second_quote_index]
                                    if int(error_order) < min:
                                        min = int(error_order)
                                        error_one = fail_rule[i]["error_rules_info"]
                                print("this test case failed：")
                                print(error_one + "failed")
                if single_test_success:
                    already_passed_testcase = list(passed_testcase)
                    checker_test.create_test(rule_path, checker)
                    test_output, test_success = checker_test.run_tests(testClass)
            if test_success:
                print("pass all test cases!")

            if not length_over_max:
                finalnegativeNumber = countNegative(rule_testcase_xml_filepath)
                finaltotalNumber = countTestcases(rule_testcase_xml_filepath)
                finalpositiveNumber = finaltotalNumber - finalnegativeNumber
                print("finally pass " + str(finaltotalNumber) + " test cases")
                print("positive case " + str(finalpositiveNumber))
                print("negative case " + str(finalnegativeNumber))
                print("input token："+str(self.input_num_tokens))
                print("output token：" + str(self.output_num_tokens))
        else:
            print("initial checker generation failed, stop the execution")