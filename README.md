# Defects4j Statistics

## Research Questions
There are 3 research questions we are planned to answer in this work. 
Each research question have its own .py (`rq1_h1.py, rq2_h1.py, rq3_h1.py, rq3_h2.py`) script to start the experiment.

## Configuring the experiments
The properties file `project_details.properties` will allow us to control the test set size, which Defects4J fault has to include in the experiment, Which fault version has to be considered for the analysis.
below are properties file explained,
* test_suite_coverage_percentage
    * Indicates for which coverage score we have to generate test suite.
* test_suite_size
    * Indicates number of testsuites we have to create.
* project_list
    * Indicates which Defects4J projects are added for the current analysis.
* Cli, Codec, ... Math 
    * Indicates for a Defets4J fault, which versions are included for analysis.
* defects4j_project_path
    * Current exported Defects4J project path.
