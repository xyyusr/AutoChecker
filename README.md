# AutoChecker

AutoChecker is a tool to automatically generate checker for static analyzers supported by LLM and based on textual description and test suite of the rule.

# Repository Contents

## Files
+ **Meta-op Set.xlsx**: The Meta-Op Set that only contains meta-operation natural language description.
+ **overview.png**: The overview of our approach.
+ **requirement.txt**: Runtime dependencies of this repository.
+ **statistics.xlsx**: The original data of answering RQ1,RQ2,RQ3 in paper.

## Directories

+ **base**: `Classified_128rules.md` lists PMD's built-in all 128 rules. Others files are auxiliary files that will be called while running: 
  + `Meta_Op_DB.json`: content of Meta-Op DB.
  + `PMD_Custom_API_DB.json`: content of Custom-API DB.
  + Both of them are database to retrieve with checking logic.
  + `PMD-Style-ASTParser.jar`: the PMD-Style AST parser which is used to parse source code to its AST.
+ **experiment**: `Experimental_20rules.json` contains 20 experimental rules. Directories it contains are:
  + `experimental-20rules-test-suite` contains 20 rules' test suite.
  + `ablation`: execution file and results of ablation experiment.
  + `autochecker`: the results of AutoChecker evaluation experiment.
  + `baselines` the execution file and results of baselines experiment.
+ **generator**: AutoChecker-related execution files.
+ **practice**: Detailed data about RQ4. 
  + Files ended with ".xml": additionally added test cases in practice.
  + Files ended with ".txt": the augmented checker after iterating those added test cases.