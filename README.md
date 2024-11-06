# AutoChecker

AutoChecker is a tool to automatically generate checker for static analyzers supported by LLM and based on textual description and test suite of the rule.

## Repository Contents

### Directory `tool`
+ `Classified_128rules.md` lists PMD's built-in all 128 rules.
+ `Meta-op Set.xlsx`: The Meta-Op Set that only contains meta-operation natural language description.
+ `Meta_Op_DB.json`: Content of Meta-Op DB.
+ `PMD_Custom_API_DB.json`: Content of Custom-API DB.
+ `PMD-Style-ASTParser.jar`: The PMD-Style AST parser which is used to parse source code to its AST.
+ `generator`: The source code of AutoChecker.
+ `statistics.xlsx`: The original data of answering RQ1,RQ2,RQ3 in paper.


### Directory `experiment`
+ experimental rules: `Experimental_20rules.json`.
+ rules-related test case set: `experimental-20rules-test-suite`.
+ `ablation`: Execution file and results of ablation experiment.
+ `baselines`: Execution file and results of baselines experiment.
+ `autochecker`: The results of AutoChecker evaluation experiment.
+ `statistics.xlsx`: The detailed data of answering RQ1,RQ2,RQ3 in paper.
+ `practice`: Detailed data about RQ4. 
  + Files ended with ".xml": Additionally added test cases in practice.
  + Files ended with ".txt": The augmented checker after iterating those added test cases.

`requirement.txt`: Runtime dependencies of this repository.